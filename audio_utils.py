import numpy as np
import io
from pydub import AudioSegment

def apply_digital_gain(audio_bytes, gain_db):
    """
    Applies digital gain using pydub. 
    Handles WebM, OGG, and WAV automatically.
    """
    if gain_db == 0:
        return audio_bytes
        
    # Load audio from bytes (pydub handles the format detection)
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    
    # Apply gain 
    processed_audio = audio + gain_db
    
    # Export back to WAV bytes for Whisper
    out_io = io.BytesIO()
    processed_audio.export(out_io, format="wav")
    return out_io.getvalue()

def is_above_noise_floor(audio_bytes, threshold_db=-40):
    """
    A simple Noise Gate. Checks if the average dBFS is above the threshold.
    """
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        # dBFS is 'Decibels relative to Full Scale' (0 is max volume)
        current_db = audio.dBFS
        return current_db > threshold_db
    except Exception as e:
        print(f"Gate Error: {e}")
        return True # Default to True so we don't accidentally block valid audio