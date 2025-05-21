import streamlit as st
import os
from VoiceEnroller import VoiceEnroller
from VoiceAuthenticator import VoiceAuthenticator
import time
import tempfile

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
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = tempfile.mkdtemp()

# Initialize authenticator and enroller
enroller = VoiceEnroller()
authenticator = VoiceAuthenticator()

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
                with st.spinner("Recording in progress..."):
                    st.info("Speak your passphrase when ready...")
                    time.sleep(1)  # Give user time to prepare
                    
                    # Record audio using enroller's method
                    audio_path = enroller.record_audio()
                    if audio_path:
                        # Enroll user
                        success, message = enroller.enroll_user(username, audio_path, passphrase)
                        
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
                            st.info("Tips: Speak clearly and exactly match the passphrase text.")

elif page == "Authenticate":
    st.header("Authenticate User")
    
    with st.form("authentication_form"):
        username = st.text_input("Username")
        submitted = st.form_submit_button("Start Recording")
        
        if submitted:
            if not username:
                st.error("Please enter username")
            else:
                with st.spinner("Recording in progress..."):
                    st.info("Speak your passphrase when ready...")
                    time.sleep(1)  # Give user time to prepare
                    
                    # Record audio using authenticator's method
                    audio_path = authenticator.record_audio()
                    if audio_path:
                        # Authenticate user
                        success, message = authenticator.authenticate(username, audio_path)
                        
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)

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