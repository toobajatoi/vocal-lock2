# Vocal Lock: Voice Authentication System

This project implements a voice authentication system using Python, Whisper for speech-to-text, and machine learning for voice feature extraction and verification. It includes both command-line and Streamlit web interfaces for user enrollment and authentication.

## Features
- **User Enrollment**: Register users with a username and a voice passphrase.
- **Voice Authentication**: Authenticate users by matching their voice and passphrase.
- **User Listing**: List all enrolled users.
- **Streamlit Web App**: User-friendly web interface for enrollment and authentication.

## Requirements
- Python 3.8+
- [Whisper](https://github.com/openai/whisper)
- numpy
- soundfile
- sounddevice
- pyAudioAnalysis
- scikit-learn
- streamlit

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line
1. **Enroll a User**
   - Run the enrollment script (see `VoiceEnroller.py` if available).
2. **Authenticate a User**
   - Use the `VoiceAuthenticator` class to authenticate with a username and a new voice sample.

### Streamlit Web App
Run the app with:
```bash
streamlit run app.py
```

Follow the on-screen instructions to enroll or authenticate users.

## Data Storage
- User data (voice features and passphrases) are stored in `voice_data/voice_data.json`.

## Notes
- Ensure your microphone is set up and accessible.
- The first time you use Whisper, it will download the model weights (requires internet connection).

## License
MIT 