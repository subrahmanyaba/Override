import google.generativeai as genai
from typing import List
import yaml
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        genai.configure(api_key=config["gemini"]["api_key"])
        self.model = genai.GenerativeModel(config["gemini"]["model"])
        self.logger = logger

    def get_song_recommendations(self, prompt: str, count: int = 5) -> List[str]:
        """Get song names from Gemini based on user prompt"""
        try:
            response = self.model.generate_content(
                f"Recommend exactly {count} songs that match this mood/description: {prompt}. "
                "Return ONLY song names separated by newlines, no numbers or extra text."
            )
            songs = [s.strip() for s in response.text.split("\n") if s.strip()]
            self.logger.info(f"Gemini recommended: {songs}")
            return songs
        except Exception as e:
            self.logger.error(f"Gemini request failed: {e}")
            raise