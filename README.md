https://github.com/user-attachments/assets/b7f3bd20-544b-47ad-a6ff-c55de285f4ac

# 💅 Sassy Weather AI 
A high-performance, personality-driven weather dashboard that integrates the OpenWeather API with local AI models for privacy-focused, character-driven forecasts.

### 🎥 The "Why" Behind the Project
This is my debut project as I pivot from a career in Film & TV Technical Post-Production into AI Engineering via Python. It represents a deep dive into bridging the gap between raw data (OpenWeather API) and natural language generation (Ollama).

My focus is on privacy-centric, local-first AI, ensuring that user data never leaves the local machine while providing a high-fidelity, interactive experience.

### 🚀 Key Features
- **API Data Handling:** Managing complex JSON structures from OpenWeather.
- **Prompt Engineering:** Tailoring multiple local AI personalities with distinct tones and contexts (sassy, classy, noob photographer).
- **Python Logic:** Solving real-world data sync and error handling challenges.
- **Error Handling:** Robust validation with sassy error messages
- **Privacy Focus:** All processing happens locally with Python +  Ollama

As a starting AI enthusiast, I am focused on **privacy-centric AI projects** that keep data local.

### 📁 Media Assets & Privacy

**Note on the /assets directory:**
This project utilizes proprietary video assets for the character "Sassy Tabby." To protect intellectual property, the /assets folder is included in the .gitignore and is not synced to this public repository.

- **To run this locally:** You must provide your own .mp4 assets (e.g., tabby_sun.mp4, tabby_rain.mp4, tabby_cloudy.mp4) in the root /assets directory.

### ✏️ Prerequisites
**Ollama:** Installed and running locally.
Note: If you have disabled Ollama's autostart, or Ollama isn't running, ensure you run 'ollama serve' in your terminal before launching this app.

**OpenWeather API Key:** You'll need a free key from OpenWeatherMap.

**LLM Model:** gemma4:26b-a4b-it-q4_K_M (changed from gpt-oss:20b (Native MXFP4)). -- main.py
               Llama-3.2-3B-Instruct-Q4_K_M.gguf -- desktop port (moved away from ollama dependence)


### ⚙️ Setup & Installation

**Environment Variables:** Create a .env file in the root directory and add:

    OPENWEATHER_API_KEY=your_key_here


**Install Dependencies:**

    pip install -r requirements.txt


🏃 Quick Start

To launch the application, run the following command in your terminal:

    streamlit run main.py


### 🧠 Architecture: Modular RAG-Lite

This project implements a Retrieval-Augmented Generation (RAG) workflow to manage AI personalities and system constraints without hard-coding text into the logic.

***The Vector (User Input):*** Intent is captured via text or local Whisper transcription.

**The Retrieval Phase:** llm_brain.py dynamically fetches .txt assets from the /personas/ directory based on UI selection.

**Hierarchical Prompt Stacking:**

**Base Layer (rules.txt):** Universal mechanical constraints and thermal logic.

**Identity Layer ({persona}.txt):** Unique tone, vocabulary, and stylistic instructions.

**Context Layer:** Live API telemetry + User query.

**Augmented Generation:** The LLM receives the "stacked" prompt to ensure character consistency.

### 🛠️ Development Environment (System Specs)

This project is optimized for local execution using the following hardware:

**CPU:** AMD Ryzen 7 9800X3D

**RAM:** 64GB DDR5 @ 6000MHz

**GPU:** NVIDIA RTX 3090 (24GB VRAM) — Crucial for running MoE models like Gemma4 locally and Whisper simultaenously.

### 🛠️ Tech Stack
- **Code:** Python
- **Brain:** Ollama (gemma4:26b-a4b-it-q4_K_M)
- **Data:** OpenWeather 5-Day Forecast API
- **Transcription:** OpenAI Whisper (Base model running on CUDA)
- **Audio:** Edge-TTS
- **Frontend:** Streamlit + Flet (for android dev)

### 📁 Directory Structure

- **/personas/:** The RAG Knowledge Base for AI characters.

- **main.py:** Main Streamlit entry point & Liquid Layout CSS. Also contains an input 'cleanser' since moving to streamlit / webui.

- **llm_brain.py:** The RAG orchestration and LLM logic.

- **weather_utils.py:** Meteorology logic and data transcoding.

- **voice_utils.py:** TTS generation and HTML audio injection.

- **santizer.py:** Original input 'cleanser' for any malicous code injections before hitting the LLM.

**Developed by a Technical Post-Production Supervisor upskilling into AI Engineering.**
