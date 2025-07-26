# gemini_client.py

import os
import json
import pdb
import re
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")  # e.g. "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"


def get_emotional_plan(prompt: str) -> dict:
    """
    Sends a prompt to Gemini API to get emotional music/visual plan.
    Returns a parsed dictionary with expected keys like:
    - current_emotion
    - target_emotion
    - mood_curve
    - music_suggestions (YouTube links)
    - visual_style
    """
    if not API_KEY:
        raise EnvironmentError("❌ GEMINI_API_KEY not found in .env or environment.")
    if not BASE_URL:
        raise EnvironmentError("❌ BASE_URL not found in .env or environment.")

    # Embed instruction + user input
    full_prompt = f"""
You are an emotion-aware music planner.
Given a user's current emotion and desired emotional goal, return ONLY a raw JSON object in the following format. Do NOT wrap it in any markdown, code block, or explanation.

{{
  "current_emotion": "tired",
  "target_emotion": "energized",
  "mood_curve": ["calm", "focused", "energized"],
  "music_suggestions": [
    "Coldplay - Paradise",
    "Daft Punk - One More Time",
    "ODESZA - A Moment Apart"
  ],
  "visual_style": {{
    "color_palette": ["blue", "orange"],
    "animation_style": "fluid"
  }}
}}

Only suggest real, public songs by title (artist + track).
Avoid meme songs like “Never Gonna Give You Up” unless highly relevant.
Make sure the song suggestions match the emotional arc.
Respond with ONLY the JSON. No markdown, no explanation, no commentary.

User Input:
{prompt}
"""


    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": API_KEY
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": full_prompt}]
            }
        ]
    }

    try:
        response = requests.post(BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        raw = response.json()

        # Extract text output from Gemini
        text = raw["candidates"][0]["content"]["parts"][0]["text"]

        # Clean up code block formatting if Gemini wraps it in ```json ... ```
        text = re.sub(r"^```(?:json)?\n?|```$", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)

        # Convert string to dict
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON returned by Gemini:\n{text}") from e

    except requests.RequestException as e:
        raise RuntimeError(f"❌ Gemini API request failed: {str(e)}")
