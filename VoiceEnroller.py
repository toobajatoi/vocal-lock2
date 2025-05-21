import os
import json
import whisper
import numpy as np
import soundfile as sf
import sounddevice as sd
from pyAudioAnalysis import ShortTermFeatures

class VoiceEnroller:
    def __init__(self, storage_path='voice_data'):
        self.storage_path = storage_path
        self.json_file = os.path.join(storage_path, 'voice_data.json')
        self.model = whisper.load_model("base")
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize JSON file if it doesn't exist
        if not os.path.exists(self.json_file):
            with open(self.json_file, 'w') as f:
                json.dump({}, f)

    def record_audio(self, output_path='input.wav', duration=5, fs=16000):
        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished
        print("Recording finished!")
        
        # Save the recording
        sf.write(output_path, recording, fs)
        return output_path

    def extract_features(self, audio_path):
        x, Fs = sf.read(audio_path)
        F, _ = ShortTermFeatures.feature_extraction(x, Fs, 0.050*Fs, 0.025*Fs)
        return np.mean(F, axis=1).tolist()  # Convert numpy array to list for JSON serialization

    def enroll_user(self, username, audio_path, passphrase):
        # Verify the passphrase
        result = self.model.transcribe(audio_path)
        if result['text'].strip().lower() != passphrase.lower():
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

    def list_enrolled_users(self):
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            return list(data.keys())
        except (json.JSONDecodeError, FileNotFoundError):
            return []
