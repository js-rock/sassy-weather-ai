import os
import asyncio
import edge_tts
import time
from playsound import playsound

def cleanup_old_files():
    """Removes any leftover speech files that aren't currently locked."""
    for file in os.listdir():
        if file.startswith("speech_") and file.endswith(".mp3"):
            try:
                os.remove(file)
            except:
                pass # Still locked? We'll catch it next time.

async def play_audio(filepath):
    """Handles the actual playback in a separate thread."""
    try:
        await asyncio.to_thread(playsound, filepath)
    except Exception as e:
        print(f"Playback Error: {e}")

async def say_text(text, voice_name):
    """The main entry point: Generate, Play, then Clean."""
    cleanup_old_files() # Clear the graveyard first
    
    unique_id = int(time.time())
    output_file = f"speech_{unique_id}.mp3"
    
    # 1. Generate
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_file)

    # 2. Play
    await play_audio(output_file)

    # 3. Final Cleanup
    cleanup_old_files()
