import streamlit as st
import os
from VoiceEnroller import VoiceEnroller
from VoiceAuthenticator import VoiceAuthenticator
import time
import tempfile
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf

# Set page config
st.set_page_config(
    page_title="Vocal Lock - Voice Authentication System",
    page_icon="🔒",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .stAlert {
        border-radius: 5px;
    }
    .recording-status {
        font-size: 1.2em;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()
if 'recording_status' not in st.session_state:
    st.session_state.recording_status = "Ready to record"

# Initialize authenticator and enroller
enroller = VoiceEnroller()
authenticator = VoiceAuthenticator()

def plot_audio_waveform(audio_path):
    # Read audio file
    data, samplerate = sf.read(audio_path)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(data)
    ax.set_title('Audio Waveform')
    ax.set_xlabel('Sample')
    ax.set_ylabel('Amplitude')
    ax.grid(True)
    
    return fig

# App title and description
st.title("🔒 Vocal Lock")
st.markdown("A secure voice authentication system that combines speech recognition and voice biometrics.")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Enroll", "Authenticate", "User List"])

if page == "Enroll":
    st.header("Enroll New User")
    
    with st.form("enrollment_form"):
        username = st.text_input("Username")
        passphrase = st.text_input("Passphrase", type="password")
        submitted = st.form_submit_button("Start Recording")
        
        if submitted:
            if not username or not passphrase:
                st.error("Please enter both username and passphrase")
            else:
                # Recording section
                st.markdown('<div class="recording-status">🎤 Recording in progress...</div>', unsafe_allow_html=True)
                st.info("Speak your passphrase when ready...")
                time.sleep(1)  # Give user time to prepare
                
                # Record audio
                audio_path = enroller.record_audio()
                
                if audio_path:
                    # Show audio waveform
                    st.pyplot(plot_audio_waveform(audio_path))
                    
                    # Enroll user
                    with st.spinner("Processing voice data..."):
                        success, message = enroller.enroll_user(username, audio_path, passphrase)
                        
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
                            st.info("""
                            Tips for better enrollment:
                            1. Speak clearly and at a normal pace
                            2. Ensure minimal background noise
                            3. Keep a consistent distance from the microphone
                            4. Try to match the passphrase exactly
                            """)

elif page == "Authenticate":
    st.header("Authenticate User")
    
    with st.form("authentication_form"):
        username = st.text_input("Username")
        submitted = st.form_submit_button("Start Recording")
        
        if submitted:
            if not username:
                st.error("Please enter username")
            else:
                # Recording section
                st.markdown('<div class="recording-status">🎤 Recording in progress...</div>', unsafe_allow_html=True)
                st.info("Speak your passphrase when ready...")
                time.sleep(1)  # Give user time to prepare
                
                # Record audio
                audio_path = authenticator.record_audio()
                
                if audio_path:
                    # Show audio waveform
                    st.pyplot(plot_audio_waveform(audio_path))
                    
                    # Authenticate user
                    with st.spinner("Verifying voice..."):
                        success, message = authenticator.authenticate(username, audio_path)
                        
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
                            st.info("""
                            Tips for better authentication:
                            1. Speak clearly and at a normal pace
                            2. Ensure minimal background noise
                            3. Keep a consistent distance from the microphone
                            4. Try to match your enrolled passphrase exactly
                            """)

else:  # User List
    st.header("Enrolled Users")
    users = authenticator.list_users()
    
    if users:
        for user in users:
            st.write(f"👤 {user}")
    else:
        st.info("No users enrolled yet.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")

# Cleanup temporary files
try:
    for file in os.listdir(st.session_state.temp_dir):
        os.remove(os.path.join(st.session_state.temp_dir, file))
except Exception as e:
    st.error(f"Error cleaning up temporary files: {str(e)}") 