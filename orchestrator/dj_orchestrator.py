import os
import logging
import numpy as np
import librosa
from typing import List, Dict, Optional
from pathlib import Path
from utils.audio_analyzer import analyze_track
from utils.file_handler import load_audio_files
from utils.audio_tools import crossfade, align_beats, save_audio

class DJOrchestrator:
    def __init__(self, config: Dict):
        self.config = config
        self.media_library = []
        self.current_bpm = config["mixing"]["default_bpm"]
        self.analyzed_tracks = {}
        self.logger = logging.getLogger(__name__)
        self._validate_config()

    def _validate_config(self):
        """Ensure required config parameters exist."""
        required_keys = {
            "media_library": ["audio_path"],
            "mixing": ["default_bpm", "max_bpm_diff", "crossfade_duration"]
        }
        for section, keys in required_keys.items():
            if section not in self.config:
                raise KeyError(f"Missing config section: {section}")
            for key in keys:
                if key not in self.config[section]:
                    raise KeyError(f"Missing config key: {section}.{key}")

    def load_media_library(self) -> List[str]:
        """Load and validate audio files from configured path."""
        audio_path = Path(self.config["media_library"]["audio_path"])
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio path not found: {audio_path}")
        
        self.media_library = load_audio_files(str(audio_path))
        self.logger.info(f"Loaded {len(self.media_library)} tracks from {audio_path}")
        return self.media_library

    def analyze_library(self) -> Dict:
        """Analyze BPM/energy for all tracks with caching."""
        self.analyzed_tracks = {}
        for track in self.media_library:
            try:
                bpm, energy = analyze_track(track)
                self.analyzed_tracks[track] = {
                    "bpm": bpm,
                    "energy": energy,
                    "audio": None  # Lazy loading
                }
            except Exception as e:
                self.logger.error(f"Analysis failed for {Path(track).name}: {e}")
        return self.analyzed_tracks

    def _adjust_bpm(self, track_path: str, target_bpm: float) -> Dict:
        """Time-stretch audio to match target BPM."""
        try:
            y, sr = librosa.load(track_path, sr=None)
            current_bpm = self.analyzed_tracks[track_path]["bpm"]
            stretch_factor = target_bpm / current_bpm
            adjusted = librosa.effects.time_stretch(y, rate=stretch_factor)
            return {"bpm": target_bpm, "audio": adjusted, "sr": sr}
        except Exception as e:
            self.logger.error(f"BPM adjustment failed for {track_path}: {e}")
            raise

    def _get_best_match(self, current_track: str) -> Optional[str]:
        """Select next track based on energy and BPM compatibility."""
        current_data = self.analyzed_tracks[current_track]
        candidates = []
        
        for track, data in self.analyzed_tracks.items():
            if track == current_track:
                continue
                
            bpm_diff = abs(current_data["bpm"] - data["bpm"])
            energy_diff = abs(current_data["energy"] - data["energy"])
            
            if bpm_diff <= self.config["mixing"]["max_bpm_diff"]:
                score = (0.7 * (1 - bpm_diff/20)) + (0.3 * (1 - energy_diff))
                candidates.append((track, score))
        
        if not candidates:
            return None
            
        return max(candidates, key=lambda x: x[1])[0]

    def mix_tracks(self, track1: str, track2: str, output_path: str = None) -> np.ndarray:
        """Crossfade two tracks with beat alignment and save output."""
        try:
            # Load audio data
            track1_data = self.analyzed_tracks[track1]
            track2_data = self.analyzed_tracks[track2]
            
            # Lazy loading of audio
            if track1_data["audio"] is None:
                track1_data["audio"], _ = librosa.load(track1, sr=None)
            if track2_data["audio"] is None:
                track2_data["audio"], _ = librosa.load(track2, sr=None)
            
            # Align beats
            if abs(track1_data["bpm"] - track2_data["bpm"]) > self.config["mixing"]["max_bpm_diff"]:
                self.logger.warning(f"BPM mismatch ({track1_data['bpm']} vs {track2_data['bpm']}), adjusting...")
                adjusted = self._adjust_bpm(track2, track1_data["bpm"])
                track2_data["audio"] = adjusted["audio"]
                track2_data["bpm"] = adjusted["bpm"]
            
            # Perform crossfade
            mixed = crossfade(
                track1_data["audio"], 
                track2_data["audio"],
                self.config["mixing"]["crossfade_duration"]
            )
            
            if output_path:
                save_audio(mixed, output_path, sr=44100)
            
            return mixed
            
        except Exception as e:
            self.logger.error(f"Mixing failed: {e}", exc_info=True)
            raise

    def run_mix_session(self, duration_minutes: int = 60, output_dir: str = "output"):
        """Run a continuous mixing session with energy-aware transitions."""
        self.analyze_library()
        if not self.analyzed_tracks:
            raise ValueError("No valid tracks to mix")
        
        os.makedirs(output_dir, exist_ok=True)
        current_track = next(iter(self.analyzed_tracks))
        mix_count = 0
        
        self.logger.info(f"Starting {duration_minutes} minute mix session...")
        
        while mix_count < duration_minutes * 2:  # Approx 2 transitions per minute
            next_track = self._get_best_match(current_track)
            if not next_track:
                self.logger.warning("No compatible tracks left!")
                break
                
            output_file = os.path.join(output_dir, f"mix_{mix_count:03d}.wav")
            self.mix_tracks(current_track, next_track, output_file)
            self.logger.info(f"Created mix #{mix_count} → {Path(next_track).name}")
            
            current_track = next_track
            mix_count += 1
        
        self.logger.info(f"Session complete! Generated {mix_count} mixes in {output_dir}")