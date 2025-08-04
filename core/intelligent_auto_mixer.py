# core/intelligent_auto_mixer.py
import os
import numpy as np
from pydub import AudioSegment
from typing import Dict, List, Tuple, Optional
import librosa
import soundfile as sf
from agent.tools.enhanced_audio_analyzer import EnhancedAudioAnalyzer

class IntelligentAutoMixer:
    """Advanced DJ mixer with intelligent track matching and mixing"""
    
    def __init__(self):
        self.analyzer = EnhancedAudioAnalyzer()
        self.mix_styles = {
            'smooth': {'crossfade_ms': 8000, 'tempo_match': True, 'key_match': True},
            'energetic': {'crossfade_ms': 4000, 'tempo_match': True, 'key_match': False},
            'dramatic': {'crossfade_ms': 2000, 'tempo_match': False, 'key_match': False},
            'extended': {'crossfade_ms': 16000, 'tempo_match': True, 'key_match': True}
        }
    
    def mix_tracks_intelligent(self, track_a_path: str, track_b_path: str, 
                             mood_context: List[str] = None,
                             mix_style: str = 'smooth',
                             output_path: str = "data/mixed/intelligent_mix.mp3") -> str:
        """Intelligently mix two tracks with advanced analysis"""
        
        print("🔍 Analyzing tracks for intelligent mixing...")
        
        # Get comprehensive analysis for both tracks
        analysis_a = self.analyzer.analyze_track(track_a_path)
        analysis_b = self.analyzer.analyze_track(track_b_path)
        
        # Calculate compatibility score
        compatibility = self._calculate_compatibility(analysis_a, analysis_b)
        print(f"🎯 Track compatibility score: {compatibility:.2f}/10")
        
        # Find optimal mix points
        mix_out_point = self._find_optimal_mix_out_point(analysis_a, analysis_b)
        mix_in_point = self._find_optimal_mix_in_point(analysis_a, analysis_b, mix_out_point)
        
        print(f"🎛️ Mix out at: {mix_out_point:.2f}s, Mix in at: {mix_in_point:.2f}s")
        
        # Load and prepare audio segments
        track_a_segment, track_b_segment = self._prepare_audio_segments(
            track_a_path, track_b_path, analysis_a, analysis_b, mix_out_point, mix_in_point
        )
        
        # Apply intelligent processing
        if self.mix_styles[mix_style]['tempo_match']:
            track_b_segment = self._match_tempo(track_b_segment, analysis_a, analysis_b)
        
        if self.mix_styles[mix_style]['key_match']:
            track_b_segment = self._match_key(track_b_segment, analysis_a, analysis_b)
        
        # Create the final mix
        final_mix = self._create_intelligent_mix(
            track_a_segment, track_b_segment, analysis_a, analysis_b, 
            mix_style, mix_out_point, mix_in_point
        )
        
        # Export with metadata
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_mix.export(output_path, format="mp3", bitrate="320k")
        
        # Save mix metadata
        self._save_mix_metadata(output_path, analysis_a, analysis_b, compatibility)
        
        print(f"✅ Intelligent mix saved to: {output_path}")
        return output_path
    
    def _calculate_compatibility(self, analysis_a: Dict, analysis_b: Dict) -> float:
        """Calculate how well two tracks will mix together (0-10 scale)"""
        score = 0.0
        
        # Tempo compatibility (0-3 points)
        tempo_diff = abs(analysis_a['tempo'] - analysis_b['tempo'])
        if tempo_diff <= 2:
            score += 3
        elif tempo_diff <= 5:
            score += 2
        elif tempo_diff <= 10:
            score += 1
        
        # Key compatibility (0-2 points)
        if analysis_a.get('camelot_key') and analysis_b.get('camelot_key'):
            key_compatibility = self._check_key_compatibility(
                analysis_a['camelot_key'], analysis_b['camelot_key']
            )
            score += key_compatibility
        
        # Energy compatibility (0-2 points)
        energy_a_avg = np.mean(analysis_a['energy_curve'])
        energy_b_avg = np.mean(analysis_b['energy_curve'])
        energy_ratio = min(energy_a_avg, energy_b_avg) / max(energy_a_avg, energy_b_avg)
        score += energy_ratio * 2
        
        # Beat strength compatibility (0-2 points)
        beat_a_avg = np.mean(analysis_a['beat_strength'])
        beat_b_avg = np.mean(analysis_b['beat_strength'])
        beat_ratio = min(beat_a_avg, beat_b_avg) / max(beat_a_avg, beat_b_avg)
        score += beat_ratio * 2
        
        # Mix point availability (0-1 point)
        if analysis_a['mix_out_points'] and analysis_b['mix_in_points']:
            score += 1
        
        return min(score, 10.0)  # Cap at 10
    
    def _check_key_compatibility(self, key_a: str, key_b: str) -> float:
        """Check if keys are compatible using Camelot wheel rules"""
        if key_a == key_b:
            return 2.0  # Perfect match
        
        # Extract number and letter
        num_a, letter_a = key_a[:-1], key_a[-1]
        num_b, letter_b = key_b[:-1], key_b[-1]
        
        try:
            num_a, num_b = int(num_a), int(num_b)
            
            # Compatible keys: same number different letter, or adjacent numbers same letter
            if num_a == num_b and letter_a != letter_b:
                return 2.0  # Relative major/minor
            elif letter_a == letter_b and abs(num_a - num_b) == 1:
                return 1.5  # Adjacent keys
            elif letter_a == letter_b and (abs(num_a - num_b) == 11):  # Wrap around (12-1)
                return 1.5  # Adjacent keys (wraparound)
            else:
                return 0.5  # Not ideal but workable
        except:
            return 0.5
    
    def _find_optimal_mix_out_point(self, analysis_a: Dict, analysis_b: Dict) -> float:
        """Find the best point to start mixing out of track A"""
        mix_out_points = analysis_a.get('mix_out_points', [])
        
        if not mix_out_points:
            # Fallback: 75% through track A
            return analysis_a['duration'] * 0.75
        
        # Score each potential mix out point
        best_point = mix_out_points[0]
        best_score = 0
        
        for point in mix_out_points:
            score = 0
            
            # Prefer points in the latter half but not too late
            track_progress = point / analysis_a['duration']
            if 0.6 <= track_progress <= 0.8:
                score += 2
            elif 0.5 <= track_progress <= 0.9:
                score += 1
            
            # Prefer points with good beat alignment
            beats_a = analysis_a.get('beats', [])
            if beats_a:
                # Find closest beat
                closest_beat = min(beats_a, key=lambda x: abs(x - point))
                if abs(closest_beat - point) < 0.1:  # Within 100ms of beat
                    score += 1
            
            if score > best_score:
                best_score = score
                best_point = point
        
        return best_point
    
    def _find_optimal_mix_in_point(self, analysis_a: Dict, analysis_b: Dict, mix_out_point: float) -> float:
        """Find the best point to start mixing in track B"""
        mix_in_points = analysis_b.get('mix_in_points', [])
        
        if not mix_in_points:
            # Fallback: after intro
            return analysis_b.get('intro_end', 8.0)
        
        # For now, use the first good mix-in point
        # In advanced version, we'd consider beat alignment with mix_out_point
        return mix_in_points[0]
    
    def _prepare_audio_segments(self, track_a_path: str, track_b_path: str,
                               analysis_a: Dict, analysis_b: Dict,
                               mix_out_point: float, mix_in_point: float) -> Tuple[AudioSegment, AudioSegment]:
        """Prepare audio segments for mixing"""
        
        # Load full tracks
        track_a = AudioSegment.from_file(track_a_path)
        track_b = AudioSegment.from_file(track_b_path)
        
        # Prepare track A: from start to some point after mix_out_point
        mix_a_end = min(len(track_a), (mix_out_point + 20) * 1000)  # 20 seconds after mix point
        track_a_segment = track_a[:int(mix_a_end)]
        
        # Prepare track B: from mix_in_point to end
        mix_b_start = max(0, (mix_in_point - 2) * 1000)  # Start 2 seconds before mix point
        track_b_segment = track_b[int(mix_b_start):]
        
        return track_a_segment, track_b_segment
    
    def _match_tempo(self, track_b: AudioSegment, analysis_a: Dict, analysis_b: Dict) -> AudioSegment:
        """Match tempo of track B to track A using time stretching"""
        tempo_a = analysis_a['tempo']
        tempo_b = analysis_b['tempo']
        
        if abs(tempo_a - tempo_b) < 2:  # Close enough
            return track_b
        
        stretch_ratio = tempo_a / tempo_b
        
        # Convert to numpy for librosa processing
        audio_data = np.array(track_b.get_array_of_samples(), dtype=np.float32)
        if track_b.channels == 2:
            audio_data = audio_data.reshape((-1, 2))
            audio_data = np.mean(audio_data, axis=1)  # Convert to mono for processing
        
        # Normalize
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Time stretch using librosa
        stretched = librosa.effects.time_stretch(audio_data, rate=stretch_ratio)
        
        # Convert back to AudioSegment
        stretched_int16 = (stretched * 32767).astype(np.int16)
        stretched_audio = AudioSegment(
            stretched_int16.tobytes(),
            frame_rate=track_b.frame_rate,
            sample_width=2,
            channels=1
        )
        
        print(f"🎵 Tempo matched: {tempo_b:.1f} → {tempo_a:.1f} BPM")
        return stretched_audio
    
    def _match_key(self, track_b: AudioSegment, analysis_a: Dict, analysis_b: Dict) -> AudioSegment:
        """Attempt basic key matching using pitch shifting"""
        key_a = analysis_a.get('camelot_key')
        key_b = analysis_b.get('camelot_key')
        
        if not key_a or not key_b or key_a == key_b:
            return track_b
        
        # Simple pitch shift calculation (this is very basic)
        # In a real implementation, you'd use more sophisticated pitch shifting
        semitone_shift = self._calculate_semitone_shift(key_a, key_b)
        
        if abs(semitone_shift) > 6:  # Don't shift more than 6 semitones
            return track_b
        
        # For now, return unchanged (pitch shifting is complex and requires specialized libraries)
        print(f"🎼 Key matching would shift {semitone_shift} semitones ({key_b} → {key_a})")
        return track_b
    
    def _calculate_semitone_shift(self, key_target: str, key_source: str) -> int:
        """Calculate semitone shift needed (simplified)"""
        # This is a simplified version - real implementation would be more complex
        key_map = {
            '1A': 0, '1B': 3, '2A': 1, '2B': 4, '3A': 2, '3B': 5,
            '4A': 3, '4B': 6, '5A': 4, '5B': 7, '6A': 5, '6B': 8,
            '7A': 6, '7B': 9, '8A': 7, '8B': 10, '9A': 8, '9B': 11,
            '10A': 9, '10B': 0, '11A': 10, '11B': 1, '12A': 11, '12B': 2
        }
        
        source_pos = key_map.get(key_source, 0)
        target_pos = key_map.get(key_target, 0)
        
        shift = target_pos - source_pos
        if shift > 6:
            shift -= 12
        elif shift < -6:
            shift += 12
            
        return shift
    
    def _create_intelligent_mix(self, track_a: AudioSegment, track_b: AudioSegment,
                               analysis_a: Dict, analysis_b: Dict,
                               mix_style: str, mix_out_point: float, mix_in_point: float) -> AudioSegment:
        """Create the final intelligent mix"""
        
        style_config = self.mix_styles[mix_style]
        crossfade_ms = style_config['crossfade_ms']
        
        # Calculate precise timing
        mix_start_ms = int(mix_out_point * 1000)
        
        # Create the mix
        if mix_start_ms + crossfade_ms < len(track_a):
            # Standard crossfade
            part_a = track_a[:mix_start_ms + crossfade_ms]
            mixed = part_a.append(track_b, crossfade=crossfade_ms)
        else:
            # Simple append if not enough time for crossfade
            part_a = track_a[:mix_start_ms]
            mixed = part_a + track_b
        
        # Apply dynamic EQ based on track characteristics
        mixed = self._apply_intelligent_eq(mixed, analysis_a, analysis_b)
        
        return mixed
    
    def _apply_intelligent_eq(self, mixed_audio: AudioSegment, analysis_a: Dict, analysis_b: Dict) -> AudioSegment:
        """Apply intelligent EQ to enhance the mix"""
        # Simple volume balancing based on energy levels
        energy_a_avg = np.mean(analysis_a['energy_curve'])
        energy_b_avg = np.mean(analysis_b['energy_curve'])
        
        # Normalize volume if there's a significant difference
        if energy_b_avg < energy_a_avg * 0.7:
            # Boost track B if it's much quieter
            mixed_audio = mixed_audio + 2  # +2dB boost
        elif energy_b_avg > energy_a_avg * 1.4:
            # Reduce track B if it's much louder
            mixed_audio = mixed_audio - 2  # -2dB reduction
        
        return mixed_audio
    
    def _save_mix_metadata(self, output_path: str, analysis_a: Dict, analysis_b: Dict, compatibility: float):
        """Save metadata about the mix"""
        metadata = {
            'track_a': {
                'path': analysis_a['file_path'],
                'tempo': analysis_a['tempo'],
                'key': analysis_a.get('camelot_key', 'Unknown'),
                'duration': analysis_a['duration']
            },
            'track_b': {
                'path': analysis_b['file_path'],
                'tempo': analysis_b['tempo'],
                'key': analysis_b.get('camelot_key', 'Unknown'),
                'duration': analysis_b['duration']
            },
            'mix_info': {
                'compatibility_score': compatibility,
                'tempo_difference': abs(analysis_a['tempo'] - analysis_b['tempo']),
                'key_compatibility': self._check_key_compatibility(
                    analysis_a.get('camelot_key', ''), analysis_b.get('camelot_key', '')
                ) if analysis_a.get('camelot_key') and analysis_b.get('camelot_key') else 0
            }
        }
        
        metadata_path = output_path.replace('.mp3', '.mix_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_mix_recommendations(self, track_path: str, available_tracks: List[str]) -> List[Dict]:
        """Get recommended tracks to mix with the given track"""
        base_analysis = self.analyzer.analyze_track(track_path)
        recommendations = []
        
        for candidate_path in available_tracks:
            if candidate_path == track_path:
                continue
                
            candidate_analysis = self.analyzer.analyze_track(candidate_path)
            compatibility = self._calculate_compatibility(base_analysis, candidate_analysis)
            
            recommendations.append({
                'track_path': candidate_path,
                'compatibility_score': compatibility,
                'tempo_diff': abs(base_analysis['tempo'] - candidate_analysis['tempo']),
                'key_match': self._check_key_compatibility(
                    base_analysis.get('camelot_key', ''), 
                    candidate_analysis.get('camelot_key', '')
                ) if base_analysis.get('camelot_key') and candidate_analysis.get('camelot_key') else 0,
                'energy_ratio': min(
                    np.mean(base_analysis['energy_curve']), 
                    np.mean(candidate_analysis['energy_curve'])
                ) / max(
                    np.mean(base_analysis['energy_curve']), 
                    np.mean(candidate_analysis['energy_curve'])
                )
            })
        
        # Sort by compatibility score
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return recommendations[:5]  # Return top 5 matches