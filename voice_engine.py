import edge_tts
import asyncio
import pygame
import os

async def say_text(text, voice_name): # We changed 'persona_choice' to 'voice_name'
    output_file = "speech.mp3"
    
    # THE FIX: Use the variable directly! 
    # No more 'if choice == "1"' logic needed here.
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_file)

    pygame.mixer.init()
    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(1)

    pygame.mixer.music.unload()
    
    try:
        if os.path.exists(output_file):
            os.remove(output_file)
    except Exception as e:
        print(f"Cleanup error: {e}")
