import os
from typing import List

def load_audio_files(directory: str) -> List[str]:
    """Load all audio files from a directory."""
    supported_formats = [".mp3", ".wav", ".flac"]
    files = []
    for file in os.listdir(directory):
        if any(file.endswith(ext) for ext in supported_formats):
            files.append(os.path.join(directory, file))
    return files