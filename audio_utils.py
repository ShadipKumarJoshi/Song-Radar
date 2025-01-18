# audio_utils.py

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import tempfile
import os

def record_audio():
    """
    Record audio using the audio_recorder_streamlit component.
    Returns the file path of the recorded audio if successful.
    """
    audio_data = audio_recorder(
        pause_threshold=4,
        sample_rate=44100,
        icon_name="fa-solid fa-microphone-lines",
        recording_color="#6aa36f" ,
        neutral_color="#e8b62c",
        icon_size="3x"
    )
    
    if audio_data:
        st.audio(audio_data)
        file_path = "song.wav"
        with open(file_path, "wb") as f:
            f.write(audio_data)  
        return file_path
    else:
        return None
