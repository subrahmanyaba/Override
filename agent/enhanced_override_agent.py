# agent/enhanced_override_agent.py
from agent.adk_base import Agent
from agent.tools.mix_planner_tool import MixPlannerTool
from core.intelligent_auto_mixer import IntelligentAutoMixer
from agent.tools.enhanced_track_fetcher import EnhancedTrackFetcher
from agent.tools.visual_gen_tool import VisualGenTool
from agent.tools.playback_agent import PlaybackAgent
import pdb
import time
from typing import Dict, List, Optional
import os

class EnhancedOverrideAgent(Agent):
    """Enhanced agent with intelligent mixing capabilities"""
    
    def __init__(self):
        super().__init__([
            MixPlannerTool(),
            VisualGenTool()
        ])
        
        # Initialize enhanced components
        self.intelligent_mixer = IntelligentAutoMixer()
        self.track_fetcher = EnhancedTrackFetcher()
        self.playback_agent = PlaybackAgent()
        
        # Performance tracking
        self.mix_history = []
        self.performance_metrics = {
            'total_mixes': 0,
            'successful_mixes': 0,
            'average_mix_time': 0,
            'user_ratings': []
        }
    
    def run_intelligent_mix(self, track_a_path: str, track_b_path: str, 
                          mood_curve: List[str], mix_style: str = 'smooth',
                          generate_visuals: bool = True, 
                          play_immediately: bool = True) -> Dict:
        """
        Run an intelligent mix with comprehensive analysis and feedback
        """
        mix_start_time = time.time()
        
        print(f"🎧 Starting intelligent mix...")
        print(f"   Style: {mix_style}")
        print(f"   Mood context: {', '.join(mood_curve)}")
        
        try:
            # Create intelligent mix
            mix_path = self.intelligent_mixer.mix_tracks_intelligent(
                track_a_path=track_a_path,
                track_b_path=track_b_path,
                mood_context=mood_curve,
                mix_style=mix_style,
                output_path=f"data/mixed/intelligent_mix_{int(time.time())}.mp3"
            )
            
            mix_duration = time.time() - mix_start_time
            
            # Generate visuals if requested
            visuals_path = None
            if generate_visuals:
                try:
                    print("🎨 Generating mood-aware visuals...")
                    visuals_path = self.tools["VisualGenTool"].run(mood_curve)
                except Exception as e:
                    print(f"⚠️ Visual generation failed: {e}")
            
            # Play mix if requested
            if play_immediately and mix_path:
                try:
                    print("🔊 Starting playback...")
                    self.playback_agent.play(mix_path)
                except Exception as e:
                    print(f"⚠️ Playback failed: {e}")
            
            # Record successful mix
            mix_result = {
                'success': True,
                'mix_path': mix_path,
                'visuals_path': visuals_path,
                'mix_duration': mix_duration,
                'mix_style': mix_style,
                'mood_context': mood_curve,
                'timestamp': time.time()
            }
            
            self._record_mix_performance(mix_result)
            
            print(f"✅ Intelligent mix complete in {mix_duration:.1f}s")
            return mix_result
            
        except Exception as e:
            print(f"❌ Mix failed: {e}")
            
            # Record failed mix
            mix_result = {
                'success': False,
                'error': str(e),
                'mix_duration': time.time() - mix_start_time,
                'mix_style': mix_style,
                'mood_context': mood_curve,
                'timestamp': time.time()
            }
            
            self._record_mix_performance(mix_result)
            return mix_result
    
    def get_track_recommendations(self, current_track_path: str, 
                                available_tracks: List[str],
                                target_mood: str = None) -> List[Dict]:
        """
        Get intelligent track recommendations based on current track
        """
        print(f"🎯 Finding recommendations for current track...")
        
        try:
            recommendations = self.intelligent_mixer.get_mix_recommendations(
                current_track_path, available_tracks
            )
            
            # Enhance recommendations with mood scoring if target provided
            if target_mood:
                enhanced_recs = []
                for rec in recommendations:
                    # Load track metadata for mood analysis
                    try:
                        track_metadata = self.track_fetcher.get_track_metadata(rec['track_path'])
                        mood_score = self._score_track_for_mood(track_metadata, target_mood)
                        
                        enhanced_rec = {
                            **rec,
                            'mood_score': mood_score,
                            'combined_score': (rec['compatibility_score'] * 0.7) + (mood_score * 0.3)
                        }
                        enhanced_recs.append(enhanced_rec)
                    except:
                        enhanced_recs.append(rec)
                
                # Re-sort by combined score
                enhanced_recs.sort(key=lambda x: x.get('combined_score', x['compatibility_score']), reverse=True)
                return enhanced_recs
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Recommendation failed: {e}")
            return []
    
    def _score_track_for_mood(self, track_metadata: Dict, target_mood: str) -> float:
        """Score how well a track matches a target mood"""
        mood_tags = track_metadata.get('mood_tags', [])
        energy_level = track_metadata.get('energy_level', 'medium')
        
        score = 0.0
        
        # Direct mood tag matches
        if target_mood.lower() in [tag.lower() for tag in mood_tags]:
            score += 5.0
        
        # Energy level compatibility
        mood_energy_map = {
            'energetic': 'high',
            'calm': 'low', 
            'upbeat': 'high',
            'relaxed': 'low',
            'focused': 'medium',
            'party': 'high',
            'chill': 'low'
        }
        
        expected_energy = mood_energy_map.get(target_mood.lower(), 'medium')
        if energy_level == expected_energy:
            score += 3.0
        elif (energy_level == 'medium' and expected_energy in ['low', 'high']):
            score += 1.5
        
        # Tempo-mood compatibility
        tempo = track_metadata.get('tempo', 120)
        if target_mood.lower() in ['energetic', 'party', 'upbeat'] and tempo > 120:
            score += 2.0
        elif target_mood.lower() in ['calm', 'relaxed', 'chill'] and tempo < 100:
            score += 2.0
        
        return min(score, 10.0)
    
    def analyze_mix_quality(self, mix_path: str) -> Dict:
        """
        Analyze the quality of a completed mix
        """
        print("🔍 Analyzing mix quality...")
        
        try:
            # Load mix metadata if available
            metadata_path = mix_path.replace('.mp3', '.mix_metadata.json')
            
            analysis = {
                'mix_path': mix_path,
                'analysis_timestamp': time.time(),
                'quality_score': 0.0,
                'technical_metrics': {},
                'recommendations': []
            }
            
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, 'r') as f:
                    mix_metadata = json.load(f)
                
                # Analyze based on metadata
                compatibility_score = mix_metadata.get('mix_info', {}).get('compatibility_score', 0)
                tempo_diff = mix_metadata.get('mix_info', {}).get('tempo_difference', 0)
                key_compatibility = mix_metadata.get('mix_info', {}).get('key_compatibility', 0)
                
                # Calculate quality score
                quality_score = 0.0
                
                # Compatibility factor (0-4 points)
                quality_score += min(compatibility_score / 2.5, 4.0)
                
                # Tempo matching (0-3 points)
                if tempo_diff <= 5:
                    quality_score += 3.0
                elif tempo_diff <= 10:
                    quality_score += 2.0
                elif tempo_diff <= 20:
                    quality_score += 1.0
                
                # Key compatibility (0-3 points)
                quality_score += min(key_compatibility * 1.5, 3.0)
                
                analysis['quality_score'] = quality_score
                analysis['technical_metrics'] = {
                    'compatibility_score': compatibility_score,
                    'tempo_difference': tempo_diff,
                    'key_compatibility': key_compatibility,
                    'track_a_info': mix_metadata.get('track_a', {}),
                    'track_b_info': mix_metadata.get('track_b', {})
                }
                
                # Generate recommendations based on analysis
                recommendations = []
                
                if tempo_diff > 10:
                    recommendations.append("Consider using tempo matching for smoother transitions")
                
                if key_compatibility < 1.0:
                    recommendations.append("Try mixing tracks in compatible keys for better harmonic blend")
                
                if compatibility_score < 5.0:
                    recommendations.append("Look for tracks with more similar energy levels and genres")
                
                analysis['recommendations'] = recommendations
            
            else:
                # Fallback analysis without metadata
                analysis['quality_score'] = 5.0  # Neutral score
                analysis['recommendations'] = ["Enable metadata generation for detailed mix analysis"]
            
            print(f"📊 Mix quality score: {analysis['quality_score']:.1f}/10")
            return analysis
            
        except Exception as e:
            print(f"❌ Mix analysis failed: {e}")
            return {
                'mix_path': mix_path,
                'error': str(e),
                'quality_score': 0.0,
                'analysis_timestamp': time.time()
            }
    
    def _record_mix_performance(self, mix_result: Dict):
        """Record mix performance for analytics"""
        self.mix_history.append(mix_result)
        self.performance_metrics['total_mixes'] += 1
        
        if mix_result['success']:
            self.performance_metrics['successful_mixes'] += 1
            
            # Update average mix time
            current_avg = self.performance_metrics['average_mix_time']
            total_successful = self.performance_metrics['successful_mixes']
            new_avg = ((current_avg * (total_successful - 1)) + mix_result['mix_duration']) / total_successful
            self.performance_metrics['average_mix_time'] = new_avg
    
    def record_user_rating(self, rating: int, feedback: str = ""):
        """Record user rating for the last mix"""
        if 1 <= rating <= 5:
            self.performance_metrics['user_ratings'].append({
                'rating': rating,
                'feedback': feedback,
                'timestamp': time.time(),
                'mix_number': len(self.mix_history)
            })
            print(f"✅ Recorded rating: {rating}/5")
        else:
            print("⚠️ Rating must be between 1 and 5")
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        metrics = self.performance_metrics
        
        success_rate = (metrics['successful_mixes'] / metrics['total_mixes'] * 100) if metrics['total_mixes'] > 0 else 0
        avg_rating = sum(r['rating'] for r in metrics['user_ratings']) / len(metrics['user_ratings']) if metrics['user_ratings'] else 0
        
        return {
            'total_mixes': metrics['total_mixes'],
            'successful_mixes': metrics['successful_mixes'],
            'success_rate': success_rate,
            'average_mix_time': metrics['average_mix_time'],
            'average_user_rating': avg_rating,
            'total_user_ratings': len(metrics['user_ratings']),
            'recent_mix_quality': [r['quality_score'] for r in self.mix_history[-5:] if r.get('quality_score')]
        }
    
    def optimize_mix_settings(self, track_a_metadata: Dict, track_b_metadata: Dict, 
                            target_mood: str = None) -> Dict:
        """
        Suggest optimal mix settings based on track analysis
        """
        print("🎛️ Optimizing mix settings...")
        
        settings = {
            'mix_style': 'smooth',  # default
            'crossfade_duration': 8000,  # ms
            'tempo_match': True,
            'key_match': False,
            'confidence': 0.5
        }
        
        try:
            # Analyze tempo compatibility
            tempo_a = track_a_metadata.get('tempo', 120)
            tempo_b = track_b_metadata.get('tempo', 120)
            tempo_diff = abs(tempo_a - tempo_b)
            
            # Analyze energy levels
            energy_a = track_a_metadata.get('energy_level', 'medium')
            energy_b = track_b_metadata.get('energy_level', 'medium')
            
            # Optimize based on analysis
            if tempo_diff <= 5:
                settings['mix_style'] = 'smooth'
                settings['crossfade_duration'] = 12000
                settings['confidence'] += 0.3
            elif tempo_diff <= 15:
                settings['mix_style'] = 'smooth'
                settings['crossfade_duration'] = 8000
                settings['confidence'] += 0.1
            else:
                settings['mix_style'] = 'dramatic'
                settings['crossfade_duration'] = 4000
                settings['tempo_match'] = True
                settings['confidence'] -= 0.2
            
            # Energy-based adjustments
            energy_map = {'low': 1, 'medium': 2, 'high': 3}
            energy_diff = abs(energy_map.get(energy_a, 2) - energy_map.get(energy_b, 2))
            
            if energy_diff >= 2:
                settings['mix_style'] = 'energetic'
                settings['crossfade_duration'] = 6000
            
            # Key compatibility check
            key_a = track_a_metadata.get('camelot_key')
            key_b = track_b_metadata.get('camelot_key')
            
            if key_a and key_b:
                # Use the mixer's key compatibility check
                key_compatibility = self.intelligent_mixer._check_key_compatibility(key_a, key_b)
                if key_compatibility >= 1.5:
                    settings['key_match'] = True
                    settings['confidence'] += 0.2
            
            # Target mood adjustments
            if target_mood:
                mood_styles = {
                    'energetic': 'energetic',
                    'party': 'energetic',
                    'calm': 'extended',
                    'relaxed': 'extended',
                    'focused': 'smooth'
                }
                
                if target_mood.lower() in mood_styles:
                    settings['mix_style'] = mood_styles[target_mood.lower()]
            
            settings['confidence'] = max(0.1, min(1.0, settings['confidence']))
            
            print(f"🎯 Optimized settings: {settings['mix_style']} style, {settings['crossfade_duration']}ms crossfade")
            print(f"   Confidence: {settings['confidence']:.1f}")
            
            return settings
            
        except Exception as e:
            print(f"⚠️ Settings optimization failed: {e}")
            return settings
    
    def run_adaptive_mix(self, track_a_path: str, track_b_path: str, 
                        mood_curve: List[str], target_mood: str = None) -> Dict:
        """
        Run a mix with adaptive settings based on track analysis
        """
        try:
            # Load track metadata
            track_a_metadata = self._load_track_metadata(track_a_path)
            track_b_metadata = self._load_track_metadata(track_b_path)
            
            if not track_a_metadata or not track_b_metadata:
                print("⚠️ Missing track metadata, using default settings")
                return self.run_intelligent_mix(track_a_path, track_b_path, mood_curve)
            
            # Optimize mix settings
            optimal_settings = self.optimize_mix_settings(
                track_a_metadata, track_b_metadata, target_mood
            )
            
            # Run mix with optimized settings
            return self.run_intelligent_mix(
                track_a_path=track_a_path,
                track_b_path=track_b_path,
                mood_curve=mood_curve,
                mix_style=optimal_settings['mix_style']
            )
            
        except Exception as e:
            print(f"❌ Adaptive mix failed: {e}")
            # Fallback to standard intelligent mix
            return self.run_intelligent_mix(track_a_path, track_b_path, mood_curve)
    
    def _load_track_metadata(self, track_path: str) -> Optional[Dict]:
        """Load track metadata from file"""
        metadata_path = track_path.replace('.mp3', '.enhanced_metadata.json')
        
        if os.path.exists(metadata_path):
            try:
                import json
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading metadata for {track_path}: {e}")
        
        return None
    
    def export_session_analysis(self, output_path: str = "data/analysis/session_analysis.json"):
        """Export detailed session analysis for improvement"""
        import json
        import os
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        analysis_data = {
            'session_timestamp': time.time(),
            'performance_summary': self.get_performance_summary(),
            'mix_history': self.mix_history,
            'detailed_metrics': {
                'mix_styles_used': {},
                'common_failures': [],
                'quality_trends': []
            }
        }
        
        # Analyze mix styles
        for mix in self.mix_history:
            style = mix.get('mix_style', 'unknown')
            if style not in analysis_data['detailed_metrics']['mix_styles_used']:
                analysis_data['detailed_metrics']['mix_styles_used'][style] = 0
            analysis_data['detailed_metrics']['mix_styles_used'][style] += 1
        
        # Identify common failure patterns
        failed_mixes = [mix for mix in self.mix_history if not mix['success']]
        for failed_mix in failed_mixes:
            error = failed_mix.get('error', 'Unknown error')
            analysis_data['detailed_metrics']['common_failures'].append(error)
        
        # Quality trends
        for i, mix in enumerate(self.mix_history):
            if mix.get('quality_score'):
                analysis_data['detailed_metrics']['quality_trends'].append({
                    'mix_number': i + 1,
                    'quality_score': mix['quality_score'],
                    'timestamp': mix.get('timestamp')
                })
        
        with open(output_path, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"📊 Session analysis exported to: {output_path}")
        return output_path