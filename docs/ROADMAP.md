### Sassy Weather AI - Development Phases

### Phase 1: The Desktop Titan (COMPLETED ✅)

- [x] API Integration (OpenWeather).

- [x] Local LLM Integration (Ollama + Gemma 4).

- [x] Local Web UI (Streamlit) formatted for "Phone View".

- [x] 5-Day Forecast "Noon Filter" & Calendar Math logic.

### Phase 2: The Audio/Visual Polish (COMPLETED ✅)

- [x] TTS Integration: edge-tts with base64 autoplay.

- [x] Persona-Voice Sync: Ava for Sassy, Andrew for Classy.

- [x] Avatar Integration: High-fidelity ComfyUI Tabby Renders.

- [x] Visual Pop: CSS entry animations and black-dip video transitions.

- [x] Security: Tightened character limits (75 chars) and isalnum sanitization.

### Phase 3: The Voice Revolution (COMPLETED ✅)

- [x] 3.1 UI/UX: Mobile-responsive "Liquid Layout" and video assets.

- [x] 3.2 Audio: Integrated streamlit-mic-recorder.

- [x] 3.3 Inference: Local Whisper transcription on RTX 3090.

### Phase 3.4: Persona Engine & Modular RAG (COMPLETED ✅)

- [x] Persona Library: Move character bios to /personas/*.txt.

- [x] Global Constraints: Create rules.txt for universal AI behavior (no emojis, length limits).

- [x] The Loader: Update llm_brain.py to "stack" prompts dynamically.

### Phase 4: Pro Audio & Mobile Transition (CURRENT 🛠️)

[x] 4.1 Digital Gain: UI slider to "boost" mic signal before Whisper.

[x] 4.2 Noise Gating: Implement decibel threshold to ignore background noise.

[ ] 4.3 Flet Preview: Set up the basic structure for the mobile version (sassy_mobile.py).

### Phase 5: External Tooling (Side-Quests) 🤖

[x] n8n Research: Completed isolated sandbox testing for CV awareness.

[ ] Portfolio Reel: Record screen capture showing the local 3090 inference.

###  Phase 6: The "Show Off" Build & Delivery 📦

- [ ] Packaging: Create .apk for Android and standalone .exe.