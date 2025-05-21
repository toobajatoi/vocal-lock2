import os
import json
import whisper
import numpy as np
import soundfile as sf
import sounddevice as sd
from pyAudioAnalysis import ShortTermFeatures
from sklearn.metrics.pairwise import cosine_similarity

class VoiceAuthenticator:
    def __init__(self, storage_path='voice_data'):
        self.storage_path = storage_path
        self.json_file = os.path.join(storage_path, 'voice_data.json')
        self.model = whisper.load_model("base")
        os.makedirs(storage_path, exist_ok=True)

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

    def extract_features(self, audio_path):
        x, Fs = sf.read(audio_path)
        F, _ = ShortTermFeatures.feature_extraction(x, Fs, 0.050*Fs, 0.025*Fs)
        return np.mean(F, axis=1)

    def verify_user_exists(self, username):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            return username in data
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def authenticate(self, username, audio_path='input.wav', threshold=0.8):
        # Check if user exists
        if not self.verify_user_exists(username):
            return False, "User not found"

        # Load user data
        with open(self.json_file, 'r') as f:
            data = json.load(f)
            user_data = data[username]

        # Verify passphrase
        phrase = self.transcribe(audio_path)
        if phrase.lower() != user_data['passphrase'].lower():
            return False, "Passphrase mismatch"

        # Verify voice
        sim = cosine_similarity(
            [self.extract_features(audio_path)],
            [user_data['vector']]
        )[0][0]

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
