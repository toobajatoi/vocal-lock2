import streamlit as st
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper
import pyAudioAnalysis.audioBasicIO as audioBasicIO
import pyAudioAnalysis.ShortTermFeatures as audioFeatureExtraction
from datetime import datetime
import json
import os
from scipy.spatial.distance import cosine
import time

class VoiceEnroller:
    def __init__(self):
        self.model = whisper.load_model("base")
        self.sample_rate = 16000
        self.duration = 5  # Recording duration in seconds
        
    def record_audio(self):
        st.write("Recording... Speak your passphrase")
        recording = sd.rec(int(self.duration * self.sample_rate),
                         samplerate=self.sample_rate,
                         channels=1)
        sd.wait()
        return recording.flatten()
    
    def extract_features(self, audio_data):
        # Save temporary file for pyAudioAnalysis
        temp_file = "temp_recording.wav"
        sf.write(temp_file, audio_data, self.sample_rate)
        
        # Extract features
        [Fs, x] = audioBasicIO.read_audio_file(temp_file)
        features, _ = audioFeatureExtraction.feature_extraction(x, Fs, 0.050*Fs, 0.025*Fs)
        
        # Clean up
        os.remove(temp_file)
        
        # Return mean of features as voiceprint
        return np.mean(features, axis=1)
    
    def transcribe(self, audio_data):
        # Save temporary file for Whisper
        temp_file = "temp_recording.wav"
        sf.write(temp_file, audio_data, self.sample_rate)
        
        # Transcribe
        result = self.model.transcribe(temp_file)
        
        # Clean up
        os.remove(temp_file)
        
        return result["text"].strip().lower()

class VoiceAuthenticator:
    def __init__(self):
        self.enroller = VoiceEnroller()
        self.threshold = 0.3  # Cosine similarity threshold
        
    def authenticate(self, audio_data, stored_data):
        # Extract features and transcribe
        features = self.enroller.extract_features(audio_data)
        text = self.enroller.transcribe(audio_data)
        
        # Compare with stored data
        stored_features = np.array(stored_data["voiceprint"])
        stored_text = stored_data["phrase"]
        
        # Calculate similarity
        similarity = 1 - cosine(features, stored_features)
        text_match = text == stored_text
        
        return similarity > self.threshold and text_match, similarity

class AccessGateController:
    def __init__(self):
        self.authenticator = VoiceAuthenticator()
        self.max_attempts = 3
        self.cooldown_time = 300  # 5 minutes in seconds
        self.attempts = 0
        self.last_attempt_time = 0
        self.stored_data = None
        
    def load_stored_data(self):
        try:
            with open("voice_data.json", "r") as f:
                self.stored_data = json.load(f)
        except FileNotFoundError:
            self.stored_data = None
    
    def save_stored_data(self, phrase, voiceprint):
        data = {
            "phrase": phrase,
            "voiceprint": voiceprint.tolist()
        }
        with open("voice_data.json", "w") as f:
            json.dump(data, f)
        self.stored_data = data
    
    def log_attempt(self, success):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("access_log.txt", "a") as f:
            f.write(f"{timestamp} - {'GRANTED' if success else 'DENIED'}\n")
    
    def check_access(self, audio_data):
        current_time = time.time()
        
        # Check cooldown
        if self.attempts >= self.max_attempts:
            if current_time - self.last_attempt_time < self.cooldown_time:
                return False, "Too many attempts. Please wait."
            self.attempts = 0
        
        self.last_attempt_time = current_time
        
        if not self.stored_data:
            return False, "No enrolled voice found"
        
        success, similarity = self.authenticator.authenticate(audio_data, self.stored_data)
        self.attempts += 1
        
        if success:
            self.attempts = 0
            self.log_attempt(True)
            return True, "Access Granted!"
        else:
            self.log_attempt(False)
            return False, "Access Denied"

def main():
    st.title("Vocalock - Voice Authentication System")
    
    controller = AccessGateController()
    controller.load_stored_data()
    
    # Sidebar for enrollment
    with st.sidebar:
        st.header("Enrollment")
        if st.button("Enroll New Voice"):
            enroller = VoiceEnroller()
            audio_data = enroller.record_audio()
            phrase = enroller.transcribe(audio_data)
            voiceprint = enroller.extract_features(audio_data)
            
            controller.save_stored_data(phrase, voiceprint)
            st.success(f"Enrolled phrase: {phrase}")
    
    # Main area for authentication
    st.header("Authentication")
    if st.button("Authenticate"):
        if not controller.stored_data:
            st.error("Please enroll a voice first")
            return
        
        enroller = VoiceEnroller()
        audio_data = enroller.record_audio()
        
        success, message = controller.check_access(audio_data)
        if success:
            st.success(message)
        else:
            st.error(message)
    
    # Display access log
    st.header("Access Log")
    try:
        with open("access_log.txt", "r") as f:
            logs = f.readlines()
            for log in logs[-5:]:  # Show last 5 entries
                st.text(log.strip())
    except FileNotFoundError:
        st.text("No access logs yet")

if __name__ == "__main__":
    main() 