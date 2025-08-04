# agent/tools/enhanced_metadata_creator.py
import os
import json
from agent.tools.enhanced_audio_analyzer import EnhancedAudioAnalyzer

def create_enhanced_metadata_for_track(track_path: str) -> str:
    """Create comprehensive metadata for a track using enhanced analysis"""
    
    if not os.path.exists(track_path):
        raise FileNotFoundError(f"Track not found: {track_path}")
    
    print(f"🔍 Creating enhanced metadata for: {os.path.basename(track_path)}")
    
    # Use enhanced analyzer
    analyzer = EnhancedAudioAnalyzer()
    analysis = analyzer.analyze_track(track_path)
    
    # Create simplified metadata for backward compatibility
    simplified_metadata = {
        'file_path': track_path,
        'duration': analysis['duration'],
        'tempo': analysis['tempo'],
        'beats': analysis['beats'][:50],  # Limit beats for file size
        'key': analysis.get('key'),
        'camelot_key': analysis.get('camelot_key'),
        'energy_level': calculate_energy_level(analysis['energy_curve']),
        'danceability': calculate_danceability(analysis),
        'mix_in_points': analysis['mix_in_points'],
        'mix_out_points': analysis['mix_out_points'],
        'intro_end': analysis['intro_end'],
        'outro_start': analysis['outro_start'],
        'segments': analysis['segments']
    }
    
    # Save simplified metadata (for backward compatibility)
    meta_path = track_path.replace(".mp3", ".meta.json")
    with open(meta_path, "w") as f:
        json.dump(simplified_metadata, f, indent=2)
    
    print(f"✅ Enhanced metadata saved to: {meta_path}")
    return meta_path

def calculate_energy_level(energy_curve):
    """Calculate overall energy level (1-10 scale)"""
    import numpy as np
    avg_energy = np.mean(energy_curve)
    max_energy = np.max(energy_curve)
    
    # Normalize to 1-10 scale
    energy_score = min(10, max(1, (avg_energy / max_energy) * 10))
    return round(energy_score, 2)

def calculate_danceability(analysis):
    """Calculate danceability score based on various factors"""
    import numpy as np
    
    score = 0.0
    
    # Tempo factor (ideal range 120-140 BPM)
    tempo = analysis['tempo']
    if 120 <= tempo <= 140:
        score += 3
    elif 100 <= tempo <= 160:
        score += 2
    elif 80 <= tempo <= 180:
        score += 1
    
    # Beat strength consistency
    beat_strength = analysis['beat_strength']
    if beat_strength:
        consistency = 1 - (np.std(beat_strength) / np.mean(beat_strength))
        score += consistency * 3
    
    # Energy level
    energy_avg = np.mean(analysis['energy_curve'])
    energy_normalized = min(1.0, energy_avg / np.max(analysis['energy_curve']))
    score += energy_normalized * 2
    
    # Rhythmic regularity (based on beat intervals)
    beats = analysis['beats']
    if len(beats) > 3:
        intervals = np.diff(beats)
        interval_consistency = 1 - (np.std(intervals) / np.mean(intervals))
        score += interval_consistency * 2
    
    return min(10.0, max(0.0, score))