import numpy as np
import librosa
from utils.audio_tools import crossfade, save_audio
import logging
from typing import List

logger = logging.getLogger(__name__)

class AudioMixer:
    def __init__(self, crossfade_duration: float = 5.0):
        self.crossfade_duration = crossfade_duration
        self.current_audio = None

    def mix(self, new_audio_path: str) -> np.ndarray:
        """Mix new audio with current playing track"""
        new_audio, sr = librosa.load(new_audio_path, sr=None)
        
        if self.current_audio is None:
            self.current_audio = new_audio
            return new_audio
            
        mixed = crossfade(self.current_audio, new_audio, self.crossfade_duration)
        self.current_audio = new_audio
        return mixed