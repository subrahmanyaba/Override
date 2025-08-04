# core/intelligent_session_manager.py
import random
import json
import os
from typing import List, Dict, Tuple, Optional
from gemini_client import get_emotional_plan
from agent.tools.enhanced_track_fetcher import EnhancedTrackFetcher
from core.intelligent_auto_mixer import IntelligentAutoMixer

class IntelligentSessionManager:
    """Enhanced session manager with intelligent track selection and flow"""
    
    def __init__(self, user_prompt: str):
        self.user_prompt = user_prompt
        self.session_id = random.randint(100000, 999999)
        
        # Initialize components
        self.track_fetcher = EnhancedTrackFetcher()
        self.mixer = IntelligentAutoMixer()
        
        # Session state
        self.current_track_index = 0
        self.played_tracks = []
        self.track_history = []
        
        # Get initial plan from Gemini
        self.plan = get_emotional_plan(user_prompt)
        
        # Enhanced tracking
        self.session_data = {
            'user_prompt': user_prompt,
            'session_id': self.session_id,
            'start_time': None,
            'tracks_played': [],
            'user_feedback': [],
            'emotional_journey': [],
            'mix_quality_scores': []
        }
        
        # Pre-fetch and analyze suggested tracks
        self._prepare_track_queue()
    
    def _prepare_track_queue(self):
        """Pre-fetch and analyze tracks for better performance"""
        print("🎵 Preparing intelligent track queue...")
        
        suggested_tracks = self.plan.get("music_suggestions", [])
        
        # Batch fetch tracks for efficiency
        self.available_tracks = self.track_fetcher.batch_fetch_tracks(suggested_tracks)
        
        # Add any existing local tracks that might be good matches
        local_tracks = self.track_fetcher.get_local_tracks_metadata()
        self.available_tracks.extend(local_tracks)
        
        # Remove duplicates based on file path
        seen_paths = set()
        unique_tracks = []
        for track in self.available_tracks:
            if track['file_path'] not in seen_paths:
                unique_tracks.append(track)
                seen_paths.add(track['file_path'])
        
        self.available_tracks = unique_tracks
        
        print(f"📦 Prepared {len(self.available_tracks)} tracks for session")
    
    def next_track_pair_intelligent(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Get next optimal track pair using intelligent selection"""
        
        if len(self.available_tracks) < 2:
            print("🔄 Refreshing track queue...")
            self.refresh_plan()
            if len(self.available_tracks) < 2:
                return None, None
        
        # First track selection
        if not self.played_tracks:
            # For the first track, choose based on current emotion
            track_a = self._select_opening_track()
        else:
            # For subsequent tracks, use the last played track
            track_a = self.played_tracks[-1]
        
        # Second track selection using intelligent matching
        track_b = self._select_next_track(track_a)
        
        if not track_b:
            print("❌ Could not find suitable next track")
            return track_a, None
        
        # Update session state
        if track_a not in self.played_tracks:
            self.played_tracks.append(track_a)
        self.played_tracks.append(track_b)
        
        # Remove played tracks from available pool (except keep last 2 for potential remixing)
        if len(self.played_tracks) > 2:
            track_to_remove = self.played_tracks[-3]
            if track_to_remove in self.available_tracks:
                self.available_tracks.remove(track_to_remove)
        
        # Log the selection
        self._log_track_selection(track_a, track_b)
        
        return track_a, track_b
    
    def _select_opening_track(self) -> Optional[Dict]:
        """Select the best opening track based on current emotion"""
        current_emotion = self.plan.get('current_emotion', '').lower()
        
        # Score tracks based on how well they match the current emotion
        scored_tracks = []
        
        for track in self.available_tracks:
            score = self._score_track_for_emotion(track, current_emotion)
            scored_tracks.append((track, score))
        
        # Sort by score and return the best match
        scored_tracks.sort(key=lambda x: x[1], reverse=True)
        
        if scored_tracks:
            selected_track = scored_tracks[0][0]
            print(f"🎯 Opening with: {selected_track['title']} (emotion match: {scored_tracks[0][1]:.2f})")
            return selected_track
        
        return None
    
    def _score_track_for_emotion(self, track: Dict, emotion: str) -> float:
        """Score how well a track matches an emotion"""
        score = 0.0
        
        # Get track characteristics
        energy_level = track.get('energy_level', 'medium')
        mood_tags = track.get('mood_tags', [])
        tempo = track.get('tempo', 120)
        danceability = track.get('danceability', 0.5)
        
        # Emotion-based scoring
        emotion_mappings = {
            'tired': {'energy': 'low', 'tempo_range': (60, 100), 'moods': ['calm', 'relaxed', 'chill']},
            'sad': {'energy': 'low', 'tempo_range': (60, 90), 'moods': ['melancholic', 'emotional', 'slow']},
            'happy': {'energy': 'high', 'tempo_range': (110, 140), 'moods': ['upbeat', 'positive', 'bright']},
            'energetic': {'energy': 'high', 'tempo_range': (120, 160), 'moods': ['energetic', 'uplifting', 'fast']},
            'focused': {'energy': 'medium', 'tempo_range': (90, 120), 'moods': ['moderate', 'balanced']},
            'relaxed': {'energy': 'low', 'tempo_range': (70, 110), 'moods': ['calm', 'chill', 'relaxed']},
            'excited': {'energy': 'high', 'tempo_range': (130, 180), 'moods': ['party', 'energetic', 'uplifting']}
        }
        
        mapping = emotion_mappings.get(emotion, emotion_mappings['focused'])
        
        # Energy level match
        if energy_level == mapping['energy']:
            score += 3.0
        elif (energy_level == 'medium' and mapping['energy'] in ['low', 'high']) or \
             (mapping['energy'] == 'medium' and energy_level in ['low', 'high']):
            score += 1.5
        
        # Tempo match
        tempo_min, tempo_max = mapping['tempo_range']
        if tempo_min <= tempo <= tempo_max:
            score += 2.0
        elif tempo_min - 20 <= tempo <= tempo_max + 20:
            score += 1.0
        
        # Mood tags match
        for mood in mapping['moods']:
            if mood in mood_tags:
                score += 1.0
        
        # Danceability bonus for energetic emotions
        if emotion in ['happy', 'energetic', 'excited'] and danceability > 0.7:
            score += 1.0
        
        return score
    
    def _select_next_track(self, current_track: Dict) -> Optional[Dict]:
        """Select the best next track using intelligent matching"""
        
        # Get target emotion from mood curve
        target_emotion = self._get_current_target_emotion()
        
        # Get recommendations from the mixer
        available_paths = [track['file_path'] for track in self.available_tracks if track != current_track]
        recommendations = self.mixer.get_mix_recommendations(current_track['file_path'], available_paths)
        
        if not recommendations:
            print("⚠️ No mix recommendations available, using fallback selection")
            return self._fallback_track_selection(current_track)
        
        # Score recommendations based on both mix compatibility and emotional journey
        scored_recommendations = []
        
        for rec in recommendations:
            # Find the full track metadata
            track_metadata = next(
                (t for t in self.available_tracks if t['file_path'] == rec['track_path']), 
                None
            )
            
            if not track_metadata:
                continue
            
            # Combine mix compatibility with emotional fit
            mix_score = rec['compatibility_score']  # 0-10 scale
            emotion_score = self._score_track_for_emotion(track_metadata, target_emotion)  # Variable scale
            
            # Normalize emotion score to 0-10 scale
            emotion_score_normalized = min(emotion_score, 10.0)
            
            # Weight the scores (60% mix compatibility, 40% emotional fit)
            combined_score = (mix_score * 0.6) + (emotion_score_normalized * 0.4)
            
            scored_recommendations.append({
                'track': track_metadata,
                'combined_score': combined_score,
                'mix_score': mix_score,
                'emotion_score': emotion_score_normalized,
                'compatibility_data': rec
            })
        
        # Sort by combined score
        scored_recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
        
        if scored_recommendations:
            best_match = scored_recommendations[0]
            print(f"🎯 Next track: {best_match['track']['title']}")
            print(f"   Mix compatibility: {best_match['mix_score']:.1f}/10")
            print(f"   Emotional fit: {best_match['emotion_score']:.1f}/10")
            print(f"   Combined score: {best_match['combined_score']:.1f}/10")
            
            return best_match['track']
        
        return self._fallback_track_selection(current_track)
    
    def _get_current_target_emotion(self) -> str:
        """Get the current target emotion based on the mood curve progression"""
        mood_curve = self.plan.get('mood_curve', [])
        
        if not mood_curve:
            return self.plan.get('target_emotion', 'happy')
        
        # Determine position in the emotional journey
        progress = len(self.played_tracks) / max(len(mood_curve), 1)
        progress = min(progress, 1.0)
        
        # Select emotion based on progress through mood curve
        curve_index = int(progress * (len(mood_curve) - 1)) if len(mood_curve) > 1 else 0
        current_target = mood_curve[curve_index] if curve_index < len(mood_curve) else mood_curve[-1]
        
        return current_target.lower()
    
    def _fallback_track_selection(self, current_track: Dict) -> Optional[Dict]:
        """Fallback track selection when intelligent matching fails"""
        # Remove current track and already played tracks
        available = [t for t in self.available_tracks if t != current_track and t not in self.played_tracks[-2:]]
        
        if not available:
            # If we've run out, allow replaying older tracks
            available = [t for t in self.available_tracks if t != current_track]
        
        if available:
            # Simple selection based on energy progression
            target_emotion = self._get_current_target_emotion()
            scored_tracks = [(t, self._score_track_for_emotion(t, target_emotion)) for t in available]
            scored_tracks.sort(key=lambda x: x[1], reverse=True)
            return scored_tracks[0][0]
        
        return None
    
    def _log_track_selection(self, track_a: Dict, track_b: Dict):
        """Log track selection for analysis and improvement"""
        selection_log = {
            'track_a': {
                'title': track_a['title'],
                'file_path': track_a['file_path'],
                'tempo': track_a.get('tempo'),
                'energy_level': track_a.get('energy_level'),
                'key': track_a.get('camelot_key')
            },
            'track_b': {
                'title': track_b['title'],
                'file_path': track_b['file_path'],
                'tempo': track_b.get('tempo'),
                'energy_level': track_b.get('energy_level'),
                'key': track_b.get('camelot_key')
            },
            'selection_context': {
                'current_emotion': self.plan.get('current_emotion'),
                'target_emotion': self._get_current_target_emotion(),
                'session_progress': len(self.played_tracks) / 10  # Assume 10-track session
            }
        }
        
        self.track_history.append(selection_log)
    
    def refresh_plan(self):
        """Refresh the emotional plan and track queue"""
        print("🌀 Refreshing intelligent plan...")
        
        # Get new plan from Gemini
        self.plan = get_emotional_plan(self.user_prompt)
        
        # Fetch new tracks while keeping some existing ones
        new_suggestions = self.plan.get("music_suggestions", [])
        new_tracks = self.track_fetcher.batch_fetch_tracks(new_suggestions)
        
        # Merge with existing tracks (keep some variety)
        existing_tracks = [t for t in self.available_tracks if t not in self.played_tracks[-3:]]
        self.available_tracks = new_tracks + existing_tracks[:5]  # Keep 5 old tracks
        
        # Update mood curve and visual style
        self.mood_curve = self.plan.get("mood_curve", [])
        self.visual_style = self.plan.get("visual_style", {})
    
    def update_prompt(self, new_prompt: str):
        """Update the session prompt and refresh accordingly"""
        print(f"🔄 Updating session prompt to: {new_prompt}")
        self.user_prompt = new_prompt
        
        # Log the change in emotional direction
        self.session_data['emotional_journey'].append({
            'timestamp': len(self.played_tracks),
            'old_prompt': self.session_data['user_prompt'],
            'new_prompt': new_prompt,
            'trigger': 'user_request'
        })
        
        self.refresh_plan()
    
    def get_visual_mood(self) -> List[str]:
        """Get current visual mood for the visual generator"""
        mood_curve = self.plan.get("mood_curve", [])
        
        if not mood_curve:
            return ["ambient"]
        
        # Return current position in mood curve plus next 2 positions for smooth transitions
        progress = len(self.played_tracks) / max(len(mood_curve), 1)
        progress = min(progress, 1.0)
        
        current_index = int(progress * (len(mood_curve) - 1))
        
        visual_moods = []
        for i in range(current_index, min(current_index + 3, len(mood_curve))):
            visual_moods.append(mood_curve[i])
        
        return visual_moods if visual_moods else ["ambient"]
    
    def get_session_id(self) -> int:
        return self.session_id
    
    def get_session_stats(self) -> Dict:
        """Get comprehensive session statistics"""
        stats = {
            'session_id': self.session_id,
            'tracks_played': len(self.played_tracks),
            'current_emotion': self.plan.get('current_emotion'),
            'target_emotion': self.plan.get('target_emotion'),
            'average_mix_quality': sum(self.session_data['mix_quality_scores']) / len(self.session_data['mix_quality_scores']) if self.session_data['mix_quality_scores'] else 0,
            'emotional_progression': self._analyze_emotional_progression(),
            'tempo_progression': self._analyze_tempo_progression(),
            'energy_progression': self._analyze_energy_progression()
        }
        
        return stats
    
    def _analyze_emotional_progression(self) -> Dict:
        """Analyze how emotions have progressed through the session"""
        if len(self.played_tracks) < 2:
            return {'progression': 'insufficient_data'}
        
        # Analyze mood tags progression
        mood_progression = []
        for track in self.played_tracks:
            mood_tags = track.get('mood_tags', [])
            mood_progression.append(mood_tags)
        
        return {
            'progression': 'analyzed',
            'mood_evolution': mood_progression,
            'consistency': self._calculate_mood_consistency(mood_progression)
        }
    
    def _analyze_tempo_progression(self) -> Dict:
        """Analyze tempo changes throughout the session"""
        tempos = [track.get('tempo', 120) for track in self.played_tracks]
        
        if len(tempos) < 2:
            return {'progression': 'insufficient_data'}
        
        tempo_changes = [tempos[i+1] - tempos[i] for i in range(len(tempos)-1)]
        
        return {
            'start_tempo': tempos[0],
            'current_tempo': tempos[-1],
            'average_change': sum(tempo_changes) / len(tempo_changes),
            'biggest_jump': max(abs(change) for change in tempo_changes),
            'progression_smoothness': self._calculate_smoothness(tempo_changes)
        }
    
    def _analyze_energy_progression(self) -> Dict:
        """Analyze energy level changes throughout the session"""
        energy_levels = [track.get('energy_level', 'medium') for track in self.played_tracks]
        
        energy_map = {'very_low': 1, 'low': 2, 'medium': 3, 'high': 4}
        energy_values = [energy_map.get(level, 3) for level in energy_levels]
        
        if len(energy_values) < 2:
            return {'progression': 'insufficient_data'}
        
        return {
            'start_energy': energy_levels[0],
            'current_energy': energy_levels[-1],
            'energy_arc': energy_values,
            'trend': 'increasing' if energy_values[-1] > energy_values[0] else 'decreasing' if energy_values[-1] < energy_values[0] else 'stable'
        }
    
    def _calculate_mood_consistency(self, mood_progression: List[List[str]]) -> float:
        """Calculate how consistent the mood progression is"""
        if len(mood_progression) < 2:
            return 1.0
        
        # Calculate overlap between consecutive mood sets
        overlaps = []
        for i in range(len(mood_progression) - 1):
            current_moods = set(mood_progression[i])
            next_moods = set(mood_progression[i + 1])
            
            if not current_moods or not next_moods:
                overlap = 0
            else:
                intersection = len(current_moods.intersection(next_moods))
                union = len(current_moods.union(next_moods))
                overlap = intersection / union if union > 0 else 0
            
            overlaps.append(overlap)
        
        return sum(overlaps) / len(overlaps)
    
    def _calculate_smoothness(self, changes: List[float]) -> float:
        """Calculate how smooth a progression is (lower variance = smoother)"""
        if not changes:
            return 1.0
        
        avg_change = sum(changes) / len(changes)
        variance = sum((change - avg_change) ** 2 for change in changes) / len(changes)
        
        # Convert to 0-1 scale where 1 is smoothest
        return 1 / (1 + variance / 100)  # Normalize variance
    
    def record_user_feedback(self, feedback: str, rating: Optional[int] = None):
        """Record user feedback for improving future selections"""
        feedback_entry = {
            'timestamp': len(self.played_tracks),
            'feedback': feedback,
            'rating': rating,
            'current_tracks': [track['title'] for track in self.played_tracks[-2:]] if len(self.played_tracks) >= 2 else []
        }
        
        self.session_data['user_feedback'].append(feedback_entry)
    
    def save_session_data(self, output_dir: str = "data/sessions"):
        """Save session data for analysis and improvement"""
        os.makedirs(output_dir, exist_ok=True)
        
        session_file = os.path.join(output_dir, f"session_{self.session_id}.json")
        
        # Prepare session data for saving
        save_data = {
            **self.session_data,
            'final_stats': self.get_session_stats(),
            'track_history': self.track_history,
            'played_tracks': [
                {
                    'title': track['title'],
                    'file_path': track['file_path'],
                    'tempo': track.get('tempo'),
                    'energy_level': track.get('energy_level'),
                    'mood_tags': track.get('mood_tags', [])
                }
                for track in self.played_tracks
            ]
        }
        
        with open(session_file, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"💾 Session data saved to: {session_file}")
        return session_file