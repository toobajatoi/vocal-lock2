import os
import json
import whisper
import numpy as np
import soundfile as sf
import sounddevice as sd
from pyAudioAnalysis import ShortTermFeatures
from scipy.signal import butter, filtfilt
import librosa

class VoiceEnroller:
    def __init__(self, storage_path='voice_data'):
        self.storage_path = storage_path
        self.json_file = os.path.join(storage_path, 'voice_data.json')
        self.model = whisper.load_model("base", device="cpu")
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize JSON file if it doesn't exist
        if not os.path.exists(self.json_file):
            with open(self.json_file, 'w') as f:
                json.dump({}, f)

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
        
        # Ensure all features are 1D arrays
        basic_features = np.mean(F, axis=1)
        mfcc_features = np.mean(mfccs, axis=1)
        centroid_feature = np.array([np.mean(spectral_centroid)])
        rolloff_feature = np.array([np.mean(spectral_rolloff)])
        zcr_feature = np.array([np.mean(zero_crossing_rate)])
        
        # Combine all features
        features = np.concatenate([
            basic_features,  # Basic features
            mfcc_features,  # MFCCs
            centroid_feature,  # Spectral centroid
            rolloff_feature,  # Spectral rolloff
            zcr_feature  # Zero crossing rate
        ])
        
        return features.tolist()

    def record_audio(self, output_path='input.wav', duration=5, fs=16000):
        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        print("Recording finished!")
        
        # Save the recording
        sf.write(output_path, recording, fs)
        return output_path

    def enroll_user(self, username, audio_path, passphrase):
        # Verify the passphrase
        result = self.model.transcribe(audio_path)
        transcribed_text = result['text'].strip().lower()
        expected_text = passphrase.lower()
        
        # More flexible text matching
        if not self._text_matches(transcribed_text, expected_text):
            return False, "Passphrase mismatch during enrollment"

        # Extract voice features
        voice_vector = self.extract_features(audio_path)
        
        # Load existing data
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
        
        # Add new user data
        data[username] = {
            'vector': voice_vector,
            'passphrase': passphrase
        }
        
        # Save updated data
        with open(self.json_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        return True, f"Successfully enrolled user: {username}"

    def _text_matches(self, transcribed, expected):
        # Remove punctuation and extra spaces
        transcribed = ''.join(c for c in transcribed if c.isalnum() or c.isspace())
        expected = ''.join(c for c in expected if c.isalnum() or c.isspace())
        
        # Split into words
        transcribed_words = transcribed.split()
        expected_words = expected.split()
        
        # Check if all expected words are present in transcription
        return all(word in transcribed_words for word in expected_words)

    def list_enrolled_users(self):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            return list(data.keys())
        except (json.JSONDecodeError, FileNotFoundError):
            return []
