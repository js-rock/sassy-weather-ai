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

### Phase 4: Enterprise Automation (n8n + Docker) 🛠️

- [ ] 4.1 Infrastructure: Set up Docker Desktop to host the n8n Community Edition.

- [ ] 4.2 The Bridge: Modify main.py to send weather data to n8n via HTTP Webhooks.

- [ ] 4.3 Visual Workflow: Build a node-based RAG pipeline in n8n (Webhook -> Local File -> Ollama).

- [ ] 4.4 Security: Ensure the .env variables are correctly passed between Python and n8n.

### Phase 5: The Android App & Pro Audio 📱

- [ ] 5.1 Audio Logic: Implement "Digital Gain" controls and noise gating (using Post-Super knowledge) to clean up mic input before Whisper hits it.

- [ ] 5.2 Flet Transition: Begin rewriting sassy_ui.py into sassy_mobile.py using the Flet framework for a true native feel.

- [ ] 5.3 Packaging: Use Briefcase or Buildozer to package the Python code into an .apk.

###  Phase 6: The "Show Off" Build & Delivery 📦

- [ ] 6.1 Installation: Sideload onto Android phone for "Offline" testing.

- [ ] 6.2 The Pitch: Record a high-quality screen-cap/demo of the app for portfolio showcase.

- [ ] 6.3 Nuitka: Bundle the desktop version into a standalone executable.