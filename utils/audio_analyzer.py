import librosa
import numpy as np

def analyze_track(file_path: str) -> tuple:
    """Extract BPM and energy from audio file."""
    y, sr = librosa.load(file_path)
    
    # Get BPM
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    # Calculate energy (RMS)
    rms = librosa.feature.rms(y=y)
    energy = np.mean(rms)
    
    return tempo, energy

def _adjust_bpm(y: np.ndarray, sr: int, target_bpm: float) -> np.ndarray:
    """Time-stretch audio to match target BPM."""
    current_bpm = librosa.beat.tempo(y=y, sr=sr)[0]
    rate = target_bpm / current_bpm
    return librosa.effects.time_stretch(y, rate=rate)