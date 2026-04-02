# Sassy Weather AI 
A Python-based weather assistant that integrates the OpenWeather API with a local LLM (Ollama) for privacy-focused, snarky weather forecasts (also featuring other personalites).

### Why I Built This
This is my first-ever Python project and also my first AI project: LLM integration. I am currently pivoting from a career in **Film and TV Technical Post Production** into **AI Engineering**. 

This project was a deep dive into:
- **API Data Handling:** Managing complex JSON structures from OpenWeather.
- **Prompt Engineering:** Tailoring local LLM personas for consistent character output.
- **Python Logic:** Solving real-world data sync and error handling challenges.

As a starting AI enthusiast, I am focused on **privacy-centric AI projects** that keep data local.

**Prerequisites**
Ollama: Installed and running locally.
Note: If you have disabled Ollama's autostart, or Ollama isn't running, ensure you run 'ollama serve' in your terminal before launching this app.

LLM Model: gpt-oss:20b (Native MXFP4).

OpenWeather API Key: You'll need a free key from OpenWeatherMap.

Environment Variables: Create a .env file in the root directory and add:
OPENWEATHER_API_KEY=your_key_here

**Development Environment (System Specs)**
This project is optimized for local execution using the following hardware:

CPU: AMD Ryzen 7 9800X3D

RAM: 64GB DDR5 @ 6000MHz

GPU: NVIDIA RTX 3090 (24GB VRAM) — Crucial for running MoE models like GPT-OSS locally at high speed.

### Current Roadmap
- [x] Integrate OpenWeather API & Ollama.
- [x] Refine 5-day forecast "Noon Filter" logic.
- [ ] Add mic for voice input
- [ ] Fork and distill into a dedicated Android application.

### Tech Stack
- **Code:** Python
- **AI:** Ollama (gpt-oss:20b)
- **Data:** OpenWeather 5-Day Forecast API
- **Audio:** Python Voice Engine

### Key Features & Implementation
- **Modular Design:** Personas organized in separate module (sassy, classy, noob)
- **Prompt Engineering:** Multiple AI personalities with distinct tones and contexts
- **Error Handling:** Robust validation with sassy error messages
- **Privacy Focus:** All processing happens locally with Ollama