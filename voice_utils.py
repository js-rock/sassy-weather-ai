import asyncio
import base64
import os
import edge_tts

async def generate_speech_as_b64(text, voice='en-US-AvaNeural'):
    communicate = edge_tts.Communicate(text, voice)
    # Use a unique temp filename to avoid collisions if multiple requests happen
    temp_audio_file = f"temp_voice_{os.getpid()}.mp3"

    try:
        await communicate.save(temp_audio_file)
        with open(temp_audio_file, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        return b64
    finally:
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)

def get_sassy_voice_html(b64_string):
    """Returns the HTML string for an autoplaying audio element."""
    return f'<audio autoplay = "True"><source src="data:audio/mp3;base64, {b64_string}" type="audio/mp3"></audio>'

def whisper_stt_stub(audio_bytes):
        """
        Placeholder for your RTX 3090 Whisper integration.
        Soon, we will swap this for: model.transcribe(audio_bytes)
        """
        if audio_bytes:
             return "What is the weather in Seattle?"
        return None