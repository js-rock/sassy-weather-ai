Sassy Weather AI - Development Phases

Phase 1: The Desktop Titan (COMPLETED ✅)

[x] API Integration (OpenWeather).

[x] Local LLM Integration (Ollama + Gemma 4).

[x] Local Web UI (Streamlit) formatted for "Phone View".

[x] 5-Day Forecast "Noon Filter" & Calendar Math logic.

Phase 2: The Audio/Visual Polish (COMPLETED ✅)

[x] TTS Integration: edge-tts with base64 autoplay.

[x] Persona-Voice Sync: Ava for Sassy, Andrew for Classy.

[x] Avatar Integration: High-fidelity ComfyUI Tabby Renders.

[x] Visual Pop: CSS entry animations and black-dip video transitions.

[x] Security: Tightened character limits (75 chars) and isalnum sanitization.

Sassy Weather AI - Development Phases

Phase 3: The Voice Revolution (COMPLETED ✅)

[x] 3.1 UI/UX: Mobile-responsive "Liquid Layout" and video assets.

[x] 3.2 Audio: Integrated streamlit-mic-recorder.

[x] 3.3 Inference: Local Whisper transcription on RTX 3090.

Phase 3.4: Persona Engine & Modular RAG (CURRENT 🛠️)

[ ] Persona Library: Move character bios to /personas/*.txt.

[ ] Global Constraints: Create rules.txt for universal AI behavior (no emojis, length limits).

[ ] The Loader: Update llm_brain.py to "stack" prompts dynamically.

Phase 3.5: Desktop Packaging 📦

[ ] PyInstaller/Nuitka: Research bundling the Streamlit server into a standalone .exe.

Phase 4: The Android App & Pro Audio (CURRENT 🛠️)

[ ] Audio Logic: Implement "Digital Gain" controls and noise gating (using your Post-Super knowledge) to clean up mic input before Whisper hits it.

[ ] Flet Transition: Begin rewriting sassy_ui.py into sassy_mobile.py using the Flet framework for a true native feel.

[ ] Briefcase/Buildozer: Package the Python code into an .apk.

Phase 5: The "Show Off" Build 📱

[ ] Installation: Sideload onto Android phone for "Offline" testing.

[ ] The Pitch: Record a high-quality screen-cap/demo of the app for the Portfolio.