# Override – Overrule Emotions

**Override** is an agentic VJ and DJ system designed to dynamically generate music and visuals based on the user's emotions and desired mood. By interpreting user input, Override orchestrates live audio-visual experiences tailored to enhance, modulate, or transform your emotional state.  

---

## 🚀 Features

- **Emotion-driven DJing**: Generates real-time music mixes aligned with your mood goals.  
- **AI-powered VJ visuals**: Produces live, abstract visualizations synchronized with audio and emotional cues.  
- **Agentic orchestration**: Multi-agent system that plans, mixes, and visualizes tracks intelligently.  
- **Personalization & memory**: Learns user preferences over time to refine future experiences.  
- **Track automation**: Auto-download and metadata extraction for smooth integration into mixes.  
- **Interactive control**: Users can input mood, desired energy, or style, and Override adapts in real-time.  

---

## 🎛 Architecture

Override uses a modular agentic design:

1. **Emotion Planner Agent** – Analyzes user input and defines the emotional trajectory of the session.  
2. **DJ Mixer Agent** – Mixes tracks with intelligent crossfades, beat alignment, and transitions based on mood.  
3. **Visual Generator Agent** – Produces dynamic visuals that reflect the audio and emotional content.  
4. **Track Fetcher Agent** – Retrieves audio from online sources, generates metadata, and queues tracks for mixing.  

---

## ⚡ Getting Started

### Prerequisites

- Python 3.11+  
- [pydub](https://github.com/jiaaro/pydub) for audio mixing  
- ffmpeg installed and accessible in your PATH  
- yt-dlp for track fetching  

### Installation

```bash
git clone https://github.com/yourusername/override.git
cd override
pip install -r requirements.txt
