Asset Protection & IP Security Strategy

Author: Jasper
Role: Technical Post-Production Supervisor / AI Engineer

Overview

This document outlines the strategy for protecting high-value creative assets (video renders, character designs) while maintaining an open-source codebase for portfolio demonstration.

1. Intellectual Property (IP) Boundaries

Public Logic: The Python codebase, LLM prompt structures, and API integration logic are public.

Private Assets: High-resolution Tabby video renders and custom ComfyUI workflows are considered proprietary creative work.

2. Storage & Delivery Methods

To prevent "repo bloat" and protect source files, we employ the following:

Video Proxies: Using low-bitrate versions of renders for the Streamlit UI to ensure speed and discourage theft.

Git Attributes: Large files are managed via .gitattributes or excluded via .gitignore to keep the repository lean.

Cloud Hosting: Transitioning to hosted URLs (CDN) for video assets in Phase 5 to remove raw files from the GitHub repository entirely.

3. Technical Optimization (FFmpeg)

Leveraging background in Post-Production to optimize assets:

Codec: H.264/AAC for maximum compatibility.

CRF Tuning: Balancing visual fidelity with file size (Target: <2MB per loop).

Alpha Channels: Researching WebM with transparency for future UI overlays.