import os
import uuid
import threading
import subprocess
from pathlib import Path
from pydub import AudioSegment

# Create a safe temp directory manually
safe_tmp_dir = os.path.abspath("data/tmp")
Path(safe_tmp_dir).mkdir(parents=True, exist_ok=True)

class PlaybackAgent:
    def __init__(self):
        self.current_thread = None

    def play(self, file_path: str):
        def _play_audio():
            try:
                print(f"🎧 Playing {file_path} in background...")

                # Load and export as WAV to your safe directory
                audio = AudioSegment.from_file(file_path)
                temp_wav_path = os.path.join(safe_tmp_dir, f"{uuid.uuid4()}.wav")
                audio.export(temp_wav_path, format="wav")

                # Use subprocess to play via ffplay directly
                subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", temp_wav_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                os.remove(temp_wav_path)

            except Exception as e:
                print(f"❌ Playback error: {e}")

        # Run in background
        self.current_thread = threading.Thread(target=_play_audio, daemon=True)
        self.current_thread.start()
