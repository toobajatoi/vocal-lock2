import os
import sounddevice as sd
import soundfile as sf
import numpy as np
from VoiceEnroller import VoiceEnroller
from VoiceAuthenticator import VoiceAuthenticator

def record_audio(duration=5, sample_rate=16000):
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording finished!")
    return recording

def save_audio(recording, filename, sample_rate=16000):
    sf.write(filename, recording, sample_rate)
    print(f"Audio saved to {filename}")

def main():
    enroller = VoiceEnroller()
    authenticator = VoiceAuthenticator()
    
    while True:
        print("\n=== Voice Authentication System ===")
        print("1. Enroll new user")
        print("2. Authenticate user")
        print("3. List enrolled users")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            username = input("Enter username: ")
            passphrase = input("Enter passphrase: ")
            
            print("\nPlease speak your passphrase...")
            recording = record_audio()
            save_audio(recording, "enrollment.wav")
            
            success, message = enroller.enroll_user(username, "enrollment.wav", passphrase)
            print(message)
            
        elif choice == "2":
            username = input("Enter username: ")
            
            print("\nPlease speak your passphrase...")
            recording = record_audio()
            save_audio(recording, "authentication.wav")
            
            success, message = authenticator.authenticate(username, "authentication.wav")
            print(message)
            
        elif choice == "3":
            users = authenticator.list_users()
            if users:
                print("\nEnrolled users:")
                for user in users:
                    print(f"- {user}")
            else:
                print("\nNo users enrolled yet.")
                
        elif choice == "4":
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 