import os
import json
import whisper
import numpy as np
import soundfile as sf
import sounddevice as sd
from pyAudioAnalysis import ShortTermFeatures
from sklearn.metrics.pairwise import cosine_similarity
from scipy.signal import butter, filtfilt
import librosa

class VoiceAuthenticator:
    def __init__(self, storage_path='voice_data'):
        self.storage_path = storage_path
        self.json_file = os.path.join(storage_path, 'voice_data.json')
        self.model = whisper.load_model("base", device="cpu")
        self.base_threshold = 0.8
        self.adaptive_threshold = True
        os.makedirs(storage_path, exist_ok=True)

    def preprocess_audio(self, audio_data, sample_rate):
        # Normalize audio
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Apply bandpass filter (80Hz - 3000Hz) to focus on speech frequencies
        nyquist = sample_rate / 2
        low = 80 / nyquist
        high = 3000 / nyquist
        b, a = butter(4, [low, high], btype='band')
        audio_data = filtfilt(b, a, audio_data)
        
        # Remove silence
        audio_data = librosa.effects.trim(audio_data, top_db=20)[0]
        
        return audio_data

    def extract_features(self, audio_path):
        # Load and preprocess audio
        x, Fs = sf.read(audio_path)
        x = self.preprocess_audio(x, Fs)
        
        # Extract basic features
        F, _ = ShortTermFeatures.feature_extraction(x, Fs, 0.050*Fs, 0.025*Fs)
        
        # Extract additional features
        mfccs = librosa.feature.mfcc(y=x, sr=Fs, n_mfcc=13)
        spectral_centroid = librosa.feature.spectral_centroid(y=x, sr=Fs)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=x, sr=Fs)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(x)[0]
        
        # Combine all features
        features = np.concatenate([
            np.mean(F, axis=1),  # Basic features
            np.mean(mfccs, axis=1),  # MFCCs
            np.array([np.mean(spectral_centroid)]),  # Spectral centroid
            np.array([np.mean(spectral_rolloff)]),  # Spectral rolloff
            np.array([np.mean(zero_crossing_rate)])  # Zero crossing rate
        ])
        
        return features

    def record_audio(self, output_path='input.wav', duration=5, fs=16000):
        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        print("Recording finished!")
        
        # Save the recording
        sf.write(output_path, recording, fs)
        return output_path

    def transcribe(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result['text'].strip()

    def _text_matches(self, transcribed, expected):
        # Remove punctuation and extra spaces
        transcribed = ''.join(c for c in transcribed if c.isalnum() or c.isspace())
        expected = ''.join(c for c in expected if c.isalnum() or c.isspace())
        
        # Split into words
        transcribed_words = transcribed.split()
        expected_words = expected.split()
        
        # Check if all expected words are present in transcription
        return all(word in transcribed_words for word in expected_words)

    def verify_user_exists(self, username):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            return username in data
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def get_adaptive_threshold(self, username):
        if not self.adaptive_threshold:
            return self.base_threshold
            
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
                user_data = data[username]
                
            # Calculate threshold based on user's voice characteristics
            voice_vector = np.array(user_data['vector'])
            vector_norm = np.linalg.norm(voice_vector)
            
            # Adjust threshold based on vector norm
            if vector_norm > 10:
                return self.base_threshold * 0.9  # More lenient for strong voice features
            else:
                return self.base_threshold * 1.1  # More strict for weak voice features
                
        except Exception:
            return self.base_threshold

    def authenticate(self, username, audio_path='input.wav'):
        # Check if user exists
        if not self.verify_user_exists(username):
            return False, "User not found"

        # Load user data
        with open(self.json_file, 'r') as f:
            data = json.load(f)
            user_data = data[username]

        # Verify passphrase
        phrase = self.transcribe(audio_path)
        if not self._text_matches(phrase.lower(), user_data['passphrase'].lower()):
            return False, "Passphrase mismatch"

        # Extract and compare voice features
        current_features = self.extract_features(audio_path)
        stored_features = np.array(user_data['vector'])
        
        # Ensure both vectors have the same shape
        if current_features.shape != stored_features.shape:
            # Pad the shorter vector with zeros
            max_len = max(current_features.shape[0], stored_features.shape[0])
            current_features = np.pad(current_features, (0, max_len - current_features.shape[0]))
            stored_features = np.pad(stored_features, (0, max_len - stored_features.shape[0]))
        
        # Calculate similarity
        sim = cosine_similarity([current_features], [stored_features])[0][0]
        
        # Get adaptive threshold
        threshold = self.get_adaptive_threshold(username)
        
        if sim >= threshold:
            return True, f"Voice match for user {username} (sim={sim:.2f})"
        else:
            return False, f"Voice mismatch for user {username} (sim={sim:.2f})"

    def list_users(self):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            return list(data.keys())
        except (json.JSONDecodeError, FileNotFoundError):
            return []
