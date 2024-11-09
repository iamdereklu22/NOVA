TEAM_API_KEY = "sk-jM9iGBxOO_aKjZCoWlVG9A"
PROXY_ENDPOINT = "https://nova-litellm-proxy.onrender.com"
CARTESIA_API_KEY = "3b674e04-346d-444b-8c99-43e2a18d7aa2"

import openai
from openai import OpenAI

gpt = OpenAI(
        api_key=TEAM_API_KEY, # set this!!!
        base_url=PROXY_ENDPOINT # and this!!!
    )

import os
import subprocess
from cartesia import Cartesia
CARTESIA_VOICE_ID = "794f9389-aac1-45b6-b726-9d9369183238"

def wav2txt(file_path):
    """
    Converts a .wav audio file to str using OpenAI's Whisper model.

    Args:
        file_path (str): Path to the .wav file to transcribe.

    Returns:
        str: Transcribed text from the audio.
    """

    # Open the audio file
    with open(file_path, "rb") as audio_file:
        # Use Whisper API to transcribe the audio
        response = gpt.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    # Return the transcribed text
    return response.text

def txt2wav(text, file_path):
    """
    Converts text to speech using Cartesia's Sonic model and saves the audio as a .wav file.
    """
    
    voice = Cartesia(api_key=CARTESIA_API_KEY)

    # Change the encoding to 'pcm_s16le' for 16-bit PCM format
    data = voice.tts.bytes(
        model_id="sonic-english",
        transcript=text,
        voice_id=CARTESIA_VOICE_ID,
        output_format={
            "container": "wav",
            "encoding": "pcm_s16le",  # 16-bit PCM format
            "sample_rate": 44100,
        },
    )

    with open(file_path, "wb") as f:
        f.write(data)
