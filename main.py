import logging
import time
from orchestrator.gemini_client import GeminiClient
from orchestrator.youtube_dl import YouTubeDownloader
from orchestrator.mixer import AudioMixer
from utils.playlist_manager import PlaylistManager
from utils.logger import setup_logging
import sounddevice as sd
import numpy as np

class DJOrchestrator:
    def __init__(self):
        setup_logging()
        self.gemini = GeminiClient()
        self.yt = YouTubeDownloader()
        self.mixer = AudioMixer()
        self.playlist = PlaylistManager()
        self.current_prompt = None
        self.song_queue = []  # Initialize song queue

    def run(self):
        print("🎧 Gemini DJ Orchestrator - Enter prompts or 'quit'")
        while True:
            prompt = input("\nEnter mood/description: ")
            if prompt.lower() == 'quit':
                break
            
            self.current_prompt = prompt
            self._refresh_song_queue()  # Get initial songs
            self._continuous_mix()

    def _refresh_song_queue(self):
        """Get new songs from Gemini and add to queue"""
        new_songs = self.gemini.get_song_recommendations(self.current_prompt)
        self.song_queue.extend([s for s in new_songs if self.playlist.is_allowed(s)])
        
    def _continuous_mix(self):
        """Continuous mixing loop"""
        while True:
            if not self.song_queue:  # If queue is empty
                if self.playlist.needs_refresh():
                    self.playlist = PlaylistManager()  # Reset for new prompt
                self._refresh_song_queue()
                
                if not self.song_queue:  # Still empty after refresh
                    print("⚠️ No songs available. Try a different prompt.")
                    return

            song = self.song_queue.pop(0)
            audio_path = self.yt.search_and_download(song)
            
            if audio_path:
                try:
                    mixed = self.mixer.mix(audio_path)
                    sd.play(mixed, samplerate=44100)
                    self.playlist.add_played(song)
                    
                    # Wait until ~10 sec before end to prepare next
                    duration = len(mixed)/44100
                    time.sleep(max(0, duration - 10))
                except Exception as e:
                    logging.error(f"Error playing {song}: {e}")
            else:
                logging.warning(f"Failed to download {song}")

if __name__ == "__main__":
    DJOrchestrator().run()