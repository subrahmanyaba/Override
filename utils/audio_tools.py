import numpy as np
import librosa
import soundfile as sf
import logging
from pathlib import Path
from typing import Tuple, Optional
from pydub import AudioSegment
from pydub.utils import mediainfo

logger = logging.getLogger(__name__)

def load_audio(audio_path: str, sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
    """Load audio file with error handling."""
    try:
        y, sr = librosa.load(audio_path, sr=sr)
        return y, sr
    except Exception as e:
        logger.error(f"Failed to load {Path(audio_path).name}: {e}")
        raise

def save_audio(
    audio: np.ndarray, 
    output_path: str, 
    sr: int = 44100, 
    format: str = "wav"
) -> None:
    """
    Save numpy audio array to file.
    
    Args:
        audio: Audio data as numpy array
        output_path: Output file path
        sr: Sample rate
        format: File format (wav, mp3, flac)
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, audio, sr, format=format)
        logger.info(f"Saved audio to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save {output_path}: {e}")
        raise

def crossfade(
    track1: np.ndarray, 
    track2: np.ndarray, 
    duration_sec: float, 
    sr: int = 44100
) -> np.ndarray:
    """
    High-quality crossfade between two audio arrays.
    
    Args:
        track1: First audio array
        track2: Second audio array
        duration_sec: Crossfade duration in seconds
        sr: Sample rate
        
    Returns:
        Mixed audio array
    """
    try:
        # Convert to milliseconds
        fade_ms = int(duration_sec * 1000)
        
        # Convert numpy arrays to AudioSegments
        seg1 = AudioSegment(
            track1.tobytes(), 
            frame_rate=sr,
            sample_width=track1.dtype.itemsize, 
            channels=1 if len(track1.shape) == 1 else 2
        )
        seg2 = AudioSegment(
            track2.tobytes(),
            frame_rate=sr,
            sample_width=track2.dtype.itemsize,
            channels=1 if len(track2.shape) == 1 else 2
        )
        
        # Apply crossfade
        faded = seg1.append(seg2, crossfade=fade_ms)
        
        # Convert back to numpy
        return np.array(faded.get_array_of_samples(), dtype=np.float32)
    
    except Exception as e:
        logger.error(f"Crossfade failed: {e}")
        raise

def align_beats(
    audio1: np.ndarray, 
    audio2: np.ndarray, 
    sr: int,
    max_stretch: float = 0.2
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align two audio tracks by stretching within safe limits.
    
    Args:
        audio1: Reference audio
        audio2: Audio to adjust
        sr: Sample rate
        max_stretch: Maximum allowed stretch factor (20% by default)
        
    Returns:
        (audio1, adjusted_audio2)
    """
    try:
        # Get BPMs
        bpm1 = librosa.beat.tempo(y=audio1, sr=sr)[0]
        bpm2 = librosa.beat.tempo(y=audio2, sr=sr)[0]
        
        # Calculate safe stretch factor
        stretch_factor = bpm1 / bpm2
        if abs(1 - stretch_factor) > max_stretch:
            logger.warning(f"Excessive stretch required ({stretch_factor:.2f}x). Limiting to {1+max_stretch}x")
            stretch_factor = np.clip(stretch_factor, 1-max_stretch, 1+max_stretch)
        
        # Apply time-stretch
        adjusted = librosa.effects.time_stretch(audio2, rate=stretch_factor)
        return audio1, adjusted
    
    except Exception as e:
        logger.error(f"Beat alignment failed: {e}")
        raise