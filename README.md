# Vocal Lock: Voice Authentication System

This project implements a voice authentication system using Python, Whisper for speech-to-text, and machine learning for voice feature extraction and verification. It includes both command-line and Streamlit web interfaces for user enrollment and authentication.

## Features
- **User Enrollment**: Register users with a username and a voice passphrase.
- **Voice Authentication**: Authenticate users by matching their voice and passphrase.
- **User Listing**: List all enrolled users.
- **Streamlit Web App**: User-friendly web interface for enrollment and authentication.

## System Requirements
- Python 3.8+ (Python 3.10 recommended)
- Windows 10/11, macOS, or Linux
- Working microphone
- At least 4GB RAM
- Internet connection (for first-time setup)

## Dependencies
- torch==2.0.1
- openai-whisper==20231117
- pyAudioAnalysis==0.3.14
- numpy==1.24.3
- scikit-learn==1.3.0
- sounddevice==0.4.6
- soundfile==0.12.1
- pyaudio==0.2.13
- streamlit==1.28.0
- matplotlib==3.7.1

## Installation

1. Clone the repository:
```bash
git clone https://github.com/toobajatoi/vocal-lock2.git
cd vocal-lock2
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface
Run the command-line interface:
```bash
python main.py
```

The CLI provides these options:
1. Enroll new user
2. Authenticate user
3. List enrolled users
4. Exit

### Streamlit Web App
Run the web interface:
```bash
streamlit run app.py
```

The web interface will be available at `http://localhost:8501`

### User Enrollment

1. Click on "Enroll" in the sidebar
2. Enter a username
3. Enter your passphrase (this is what you'll say during recording)
4. Click "Start Recording" and speak your passphrase clearly
5. Wait for the enrollment process to complete

### Voice Authentication

1. Click on "Authenticate" in the sidebar
2. Enter your username
3. Click "Start Recording" and speak your passphrase
4. Wait for the authentication process to complete

### Listing Users

Click on "User List" in the sidebar to see all enrolled users.

## Data Storage
- User data (voice features and passphrases) are stored in `voice_data/voice_data.json`
- Temporary audio files are automatically cleaned up after use

## Troubleshooting

### Common Issues and Solutions

1. **Microphone Not Working**
   - Check if your microphone is properly connected
   - Ensure it's set as the default input device
   - Test it in your system's sound settings

2. **Installation Errors**
   - Make sure you're using Python 3.8 or higher
   - Try installing dependencies one by one if batch installation fails
   - On Windows, you might need to install Visual C++ Build Tools

3. **Streamlit App Not Starting**
   - Ensure no other Streamlit processes are running
   - Try a different port: `streamlit run app.py --server.port 8502`
   - Check if port 8501 is not being used by another application

4. **Whisper Model Download Issues**
   - Ensure you have a stable internet connection
   - The model will be downloaded on first use
   - Check your firewall settings if download fails

5. **Audio Recording Issues**
   - Speak clearly and at a normal volume
   - Ensure there's minimal background noise
   - Keep a consistent distance from the microphone

## Development

### Project Structure
```
vocal-lock/
├── app.py              # Streamlit web interface
├── main.py            # Command-line interface
├── VoiceEnroller.py   # User enrollment logic
├── VoiceAuthenticator.py  # Authentication logic
├── voice_data/        # Storage for user data
│   └── voice_data.json
└── requirements.txt   # Project dependencies
```

## License
MIT

## Contributing
Feel free to submit issues and enhancement requests! 