# agent/tools/enhanced_audio_analyzer.py
import librosa
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional
import pickle

class EnhancedAudioAnalyzer:
    """Advanced audio analysis for better DJ mixing"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        
    def analyze_track(self, audio_path: str, cache_dir: str = "data/analysis_cache") -> Dict:
        """Comprehensive track analysis with caching"""
        os.makedirs(cache_dir, exist_ok=True)
        
        # Check cache first
        cache_path = os.path.join(cache_dir, f"{os.path.basename(audio_path)}.analysis.pkl")
        if os.path.exists(cache_path):
            print(f"Loading cached analysis for {os.path.basename(audio_path)}")
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        
        print(f"Analyzing {os.path.basename(audio_path)}...")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=self.sample_rate)
        
        analysis = {
            'file_path': audio_path,
            'duration': len(y) / sr,
            'sample_rate': sr,
            
            # Tempo and rhythm
            'tempo': self._get_tempo(y, sr),
            'beats': self._get_beats(y, sr),
            'downbeats': self._get_downbeats(y, sr),
            'beat_strength': self._get_beat_strength(y, sr),
            
            # Harmonic analysis
            'key': self._estimate_key(y, sr),
            'camelot_key': None,  # Will be set after key estimation
            'chroma': self._get_chroma_features(y, sr),
            
            # Energy and dynamics
            'energy_curve': self._get_energy_curve(y, sr),
            'loudness_curve': self._get_loudness_curve(y, sr),
            'spectral_centroid': self._get_spectral_features(y, sr),
            
            # Structure analysis
            'segments': self._get_segments(y, sr),
            'intro_end': self._detect_intro_end(y, sr),
            'outro_start': self._detect_outro_start(y, sr),
            
            # Mix points
            'mix_in_points': self._find_mix_in_points(y, sr),
            'mix_out_points': self._find_mix_out_points(y, sr),
        }
        
        # Set Camelot key
        if analysis['key']:
            analysis['camelot_key'] = self._to_camelot_key(analysis['key'])
        
        # Cache the analysis
        with open(cache_path, 'wb') as f:
            pickle.dump(analysis, f)
        
        return analysis
    
    def _get_tempo(self, y: np.ndarray, sr: int) -> float:
        """Get track tempo (BPM)"""
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return float(tempo)
    
    def _get_beats(self, y: np.ndarray, sr: int) -> List[float]:
        """Get beat positions in seconds"""
        _, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
        return librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length).tolist()
    
    def _get_downbeats(self, y: np.ndarray, sr: int) -> List[float]:
        """Get downbeat positions (stronger beats)"""
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        # Estimate downbeats (every 4th beat typically)
        if len(beats) >= 4:
            downbeat_indices = beats[::4]  # Every 4th beat
            return librosa.frames_to_time(downbeat_indices, sr=sr, hop_length=self.hop_length).tolist()
        return []
    
    def _get_beat_strength(self, y: np.ndarray, sr: int) -> List[float]:
        """Get beat strength over time"""
        onset_envelope = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        times = librosa.frames_to_time(np.arange(len(onset_envelope)), sr=sr, hop_length=self.hop_length)
        return onset_envelope.tolist()
    
    def _estimate_key(self, y: np.ndarray, sr: int) -> Optional[str]:
        """Estimate musical key using chroma features"""
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        # Simple key estimation based on chroma energy
        chroma_mean = np.mean(chroma, axis=1)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Find the most prominent note
        key_idx = np.argmax(chroma_mean)
        
        # Determine if major or minor (simplified heuristic)
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        
        # Shift profiles to match detected key
        major_shifted = np.roll(major_profile, key_idx)
        minor_shifted = np.roll(minor_profile, key_idx)
        
        major_correlation = np.corrcoef(chroma_mean, major_shifted)[0, 1]
        minor_correlation = np.corrcoef(chroma_mean, minor_shifted)[0, 1]
        
        key_name = key_names[key_idx]
        mode = "major" if major_correlation > minor_correlation else "minor"
        
        return f"{key_name}_{mode}"
    
    def _to_camelot_key(self, key: str) -> str:
        """Convert musical key to Camelot notation"""
        camelot_map = {
            'C_major': '8B', 'G_major': '9B', 'D_major': '10B', 'A_major': '11B',
            'E_major': '12B', 'B_major': '1B', 'F#_major': '2B', 'C#_major': '3B',
            'G#_major': '4B', 'D#_major': '5B', 'A#_major': '6B', 'F_major': '7B',
            'A_minor': '8A', 'E_minor': '9A', 'B_minor': '10A', 'F#_minor': '11A',
            'C#_minor': '12A', 'G#_minor': '1A', 'D#_minor': '2A', 'A#_minor': '3A',
            'F_minor': '4A', 'C_minor': '5A', 'G_minor': '6A', 'D_minor': '7A'
        }
        return camelot_map.get(key, 'Unknown')
    
    def _get_chroma_features(self, y: np.ndarray, sr: int) -> List[List[float]]:
        """Get chroma features for harmonic analysis"""
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
        return chroma.T.tolist()  # Transpose for time x feature format
    
    def _get_energy_curve(self, y: np.ndarray, sr: int) -> List[float]:
        """Get energy curve over time"""
        hop_length_energy = sr // 4  # 4 measurements per second
        energy = []
        
        for i in range(0, len(y) - hop_length_energy, hop_length_energy):
            segment = y[i:i + hop_length_energy]
            energy.append(float(np.sum(segment ** 2)))
        
        return energy
    
    def _get_loudness_curve(self, y: np.ndarray, sr: int) -> List[float]:
        """Get loudness curve using RMS"""
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)[0]
        return rms.tolist()
    
    def _get_spectral_features(self, y: np.ndarray, sr: int) -> Dict:
        """Get spectral features"""
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)[0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)[0]
        
        return {
            'spectral_centroid': spectral_centroids.tolist(),
            'spectral_rolloff': spectral_rolloff.tolist(),
            'zero_crossing_rate': zero_crossing_rate.tolist()
        }
    
    def _get_segments(self, y: np.ndarray, sr: int) -> List[Dict]:
        """Detect structural segments"""
        # Simple segmentation based on spectral features
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        S = np.abs(librosa.stft(y, hop_length=self.hop_length))
        
        # Use recurrence matrix for segmentation
        try:
            segments = librosa.segment.agglomerative(chroma, k=8)  # 8 segments max
            segment_times = librosa.frames_to_time(segments, sr=sr, hop_length=self.hop_length)
            
            segments_list = []
            for i, (start, end) in enumerate(zip(segment_times[:-1], segment_times[1:])):
                segments_list.append({
                    'id': i,
                    'start': float(start),
                    'end': float(end),
                    'duration': float(end - start)
                })
            
            return segments_list
        except:
            # Fallback: simple time-based segments
            duration = len(y) / sr
            segment_length = duration / 4
            return [
                {'id': i, 'start': i * segment_length, 'end': (i + 1) * segment_length, 'duration': segment_length}
                for i in range(4)
            ]
    
    def _detect_intro_end(self, y: np.ndarray, sr: int) -> float:
        """Detect where the intro ends (full arrangement starts)"""
        # Use onset detection and energy analysis
        onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
        
        # Find the first significant sustained high-energy period
        window_size = sr // self.hop_length * 8  # 8-second window
        
        for i in range(len(onset_envelope) - window_size):
            window = onset_envelope[i:i + window_size]
            if np.mean(window) > np.mean(onset_envelope) * 1.2:  # 20% above average
                return float(librosa.frames_to_time(i, sr=sr, hop_length=self.hop_length))
        
        # Fallback: 16 seconds or 10% of track
        return min(16.0, len(y) / sr * 0.1)
    
    def _detect_outro_start(self, y: np.ndarray, sr: int) -> float:
        """Detect where the outro begins"""
        # Find where energy starts consistently decreasing
        energy = self._get_energy_curve(y, sr)
        energy_times = np.linspace(0, len(y) / sr, len(energy))
        
        # Look for sustained energy decrease in the last third of the track
        last_third_start = len(energy) * 2 // 3
        
        for i in range(last_third_start, len(energy) - 10):
            # Check if energy consistently decreases over next 10 measurements
            window = energy[i:i + 10]
            if len(window) >= 5 and all(window[j] >= window[j + 1] for j in range(len(window) - 1)):
                return float(energy_times[i])
        
        # Fallback: last 30 seconds or 15% of track
        duration = len(y) / sr
        return max(duration - 30.0, duration * 0.85)
    
    def _find_mix_in_points(self, y: np.ndarray, sr: int) -> List[float]:
        """Find good points to mix into this track"""
        beats = self._get_beats(y, sr)
        intro_end = self._detect_intro_end(y, sr)
        
        # Good mix-in points: after intro, on strong beats
        mix_points = []
        
        for beat in beats:
            if beat >= intro_end and beat <= len(y) / sr * 0.3:  # First 30% after intro
                mix_points.append(beat)
        
        return mix_points[:5]  # Return top 5 points
    
    def _find_mix_out_points(self, y: np.ndarray, sr: int) -> List[float]:
        """Find good points to mix out of this track"""
        beats = self._get_beats(y, sr)
        outro_start = self._detect_outro_start(y, sr)
        
        # Good mix-out points: before outro, on strong beats
        mix_points = []
        
        for beat in beats:
            if beat >= len(y) / sr * 0.6 and beat <= outro_start:  # Between 60% and outro
                mix_points.append(beat)
        
        return mix_points[-5:] if mix_points else []  # Return last 5 points