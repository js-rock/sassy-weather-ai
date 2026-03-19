
import edge_tts
import asyncio
import pygame
import os

async def say_text(text, persona_choice="1"):
    # 1. Map the personas to voices
    voices = {
        "1": "en-US-AvaMultilingualNeural",   # Sassy (US Fem expressive)
        "2": "en-GB-RyanNeural", # Classy (UK Male)
        "3": "en-AU-NatashaNeural"  # Noob Photographer (AU Female)
        }

    selected_voice = voices.get(persona_choice, "en-US-AnaNeural")

    output_file = "speech.mp3"

    # 2. Generate the file using edge-tts
    communicate = edge_tts.Communicate(text, selected_voice)
    await communicate.save(output_file)

    # 3. Play the file using your brand new pygame-ce
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()

        #Keep the script alive while it speaks
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

        # Stop and release the file so Windows lets us delete it
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    finally:
        pygame.mixer.quit()

        #4 The Self-Destruct (deleting the mp3)
        if os.path.exists(output_file):
            os.remove(output_file)
            

        
