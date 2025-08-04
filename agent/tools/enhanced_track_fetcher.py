# agent/tools/enhanced_track_fetcher.py
import os
import json
import hashlib
import pdb
from yt_dlp import YoutubeDL
from agent.tools.enhanced_audio_analyzer import EnhancedAudioAnalyzer
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import time

class EnhancedTrackFetcher:
    """Enhanced track fetcher with intelligent metadata generation and caching"""
    
    def __init__(self, output_dir: str = "data/tracks", cache_dir: str = "data/cache"):
        self.output_dir = output_dir
        self.cache_dir = cache_dir
        self.analyzer = EnhancedAudioAnalyzer()
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        
        # Cache for avoiding re-downloads
        self.download_cache = self._load_download_cache()
    
    def _load_download_cache(self) -> Dict:
        """Load cache of previously downloaded tracks"""
        cache_file = os.path.join(self.cache_dir, "download_cache.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_download_cache(self):
        """Save download cache"""
        cache_file = os.path.join(self.cache_dir, "download_cache.json")
        with open(cache_file, 'w') as f:
            json.dump(self.download_cache, f, indent=2)
    
    def _get_track_hash(self, query_or_url: str) -> str:
        """Generate a hash for the track query"""
        return hashlib.md5(query_or_url.encode()).hexdigest()[:12]
    
    def fetch_and_prepare_track(self, query_or_url: str, force_redownload: bool = False) -> Optional[Dict]:
        """Enhanced track fetching with comprehensive analysis"""
        
        # Check cache first
        track_hash = self._get_track_hash(query_or_url)
        if not force_redownload and track_hash in self.download_cache:
            cached_info = self.download_cache[track_hash]
            if os.path.exists(cached_info['file_path']):
                print(f"📦 Using cached track: {cached_info['title']}")
                return cached_info
        
        print(f"🎵 Fetching: {query_or_url}")
        
        # Prepare query
        if not query_or_url.startswith("http"):
            query_or_url = f"ytsearch1:{query_or_url}"
        
        # Enhanced yt-dlp options
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio/best',
            'outtmpl': f'{self.output_dir}/%(title)s_%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Higher quality
            }],
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioquality': 0,  # Best quality
        }
        
        try:
            # pdb.set_trace()
            with YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                # pdb.set_trace()
                info = ydl.extract_info(query_or_url, download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                
                # Check if we already have this specific video
                video_id = info.get('id', 'unknown')
                existing_files = [f for f in os.listdir(self.output_dir) if video_id in f and f.endswith('.mp3')]
                
                if existing_files and not force_redownload:
                    file_path = os.path.join(self.output_dir, existing_files[0])
                    print(f"📦 Found existing file: {existing_files[0]}")
                else:
                    # Download the track
                    ydl.download([query_or_url])
                    
                    # Find the downloaded file
                    title = info.get("title", "unknown").replace("/", "_").replace("\\", "_")
                    possible_files = [
                        f"{title}_{video_id}.mp3",
                        f"{title}.mp3"
                    ]
                    
                    file_path = None
                    for possible_file in possible_files:
                        full_path = os.path.join(self.output_dir, possible_file)
                        if os.path.exists(full_path):
                            file_path = full_path
                            break
                    
                    if not file_path:
                        # Find any new mp3 file with the video_id
                        all_files = os.listdir(self.output_dir)
                        matching_files = [f for f in all_files if video_id in f and f.endswith('.mp3')]
                        if matching_files:
                            file_path = os.path.join(self.output_dir, matching_files[0])
                
                if not file_path or not os.path.exists(file_path):
                    raise FileNotFoundError("Downloaded file not found")
                
                # Generate comprehensive metadata
                track_info = self._generate_comprehensive_metadata(file_path, info)
                
                # Cache the result
                self.download_cache[track_hash] = track_info
                self._save_download_cache()
                
                print(f"✅ Track ready: {track_info['title']}")
                return track_info
        
            # pdb.set_trace()
            # print("Hi")
                
        except Exception as e:
            print(f"❌ Error fetching track: {e}")
            return None
    
    def _generate_comprehensive_metadata(self, file_path: str, yt_info: Dict) -> Dict:
        """Generate comprehensive metadata including audio analysis"""
        
        print(f"🔍 Analyzing audio features...")
        
        # Get basic info from yt-dlp
        basic_info = {
            'file_path': file_path,
            'title': yt_info.get("title", "Unknown"),
            'artist': yt_info.get("uploader", "Unknown Artist"),
            'duration': yt_info.get("duration", 0),
            'webpage_url': yt_info.get("webpage_url", ""),
            'video_id': yt_info.get("id", ""),
            'upload_date': yt_info.get("upload_date", ""),
            'view_count': yt_info.get("view_count", 0),
            'like_count': yt_info.get("like_count", 0),
            'description': yt_info.get("description", "")[:500],  # First 500 chars
        }
        
        # Get comprehensive audio analysis
        try:
            audio_analysis = self.analyzer.analyze_track(file_path)
            
            # Merge basic info with audio analysis
            comprehensive_metadata = {**basic_info, **audio_analysis}
            
            # Add derived insights
            comprehensive_metadata.update({
                'energy_level': self._categorize_energy(audio_analysis['energy_curve']),
                'danceability': self._calculate_danceability(audio_analysis),
                'mix_difficulty': self._assess_mix_difficulty(audio_analysis),
                'recommended_genres': self._suggest_genres(audio_analysis),
                'mood_tags': self._generate_mood_tags(audio_analysis),
            })
            
        except Exception as e:
            print(f"⚠️ Error in audio analysis: {e}")
            # Fallback to basic metadata
            comprehensive_metadata = basic_info
            comprehensive_metadata.update({
                'energy_level': 'unknown',
                'danceability': 0.5,
                'mix_difficulty': 'medium',
                'recommended_genres': [],
                'mood_tags': []
            })
        
        # Save metadata to file
        metadata_path = file_path.replace('.mp3', '.enhanced_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(comprehensive_metadata, f, indent=2)
        
        return comprehensive_metadata
    
    def _categorize_energy(self, energy_curve: List[float]) -> str:
        """Categorize track energy level"""
        avg_energy = sum(energy_curve) / len(energy_curve) if energy_curve else 0
        energy_variance = sum((x - avg_energy) ** 2 for x in energy_curve) / len(energy_curve) if energy_curve else 0
        
        if avg_energy > 0.8:
            return 'high'
        elif avg_energy > 0.5:
            return 'medium'
        elif avg_energy > 0.2:
            return 'low'
        else:
            return 'very_low'
    
    def _calculate_danceability(self, analysis: Dict) -> float:
        """Calculate danceability score (0-1)"""
        score = 0.0
        
        # Tempo factor (optimal around 120-128 BPM)
        tempo = analysis.get('tempo', 120)
        if 110 <= tempo <= 140:
            score += 0.3
        elif 90 <= tempo <= 160:
            score += 0.2
        
        # Beat consistency
        beat_strength = analysis.get('beat_strength', [])
        if beat_strength:
            beat_consistency = 1 - (sum(abs(x - sum(beat_strength)/len(beat_strength)) for x in beat_strength) / len(beat_strength))
            score += beat_consistency * 0.4
        
        # Energy level
        energy_curve = analysis.get('energy_curve', [])
        if energy_curve:
            avg_energy = sum(energy_curve) / len(energy_curve)
            score += min(avg_energy, 0.3)
        
        return min(score, 1.0)
    
    def _assess_mix_difficulty(self, analysis: Dict) -> str:
        """Assess how difficult this track is to mix"""
        difficulty_score = 0
        
        # Tempo stability
        if analysis.get('tempo', 120) < 80 or analysis.get('tempo', 120) > 180:
            difficulty_score += 1
        
        # Key detection confidence
        if not analysis.get('key') or analysis.get('key') == 'unknown':
            difficulty_score += 1
        
        # Beat regularity
        beat_strength = analysis.get('beat_strength', [])
        if beat_strength:
            beat_variance = sum((x - sum(beat_strength)/len(beat_strength))**2 for x in beat_strength) / len(beat_strength)
            if beat_variance > 0.5:
                difficulty_score += 1
        
        # Energy consistency
        energy_curve = analysis.get('energy_curve', [])
        if energy_curve:
            energy_variance = sum((x - sum(energy_curve)/len(energy_curve))**2 for x in energy_curve) / len(energy_curve)
            if energy_variance > 0.3:
                difficulty_score += 1
        
        if difficulty_score == 0:
            return 'easy'
        elif difficulty_score <= 2:
            return 'medium'
        else:
            return 'hard'
    
    def _suggest_genres(self, analysis: Dict) -> List[str]:
        """Suggest possible genres based on audio features"""
        genres = []
        
        tempo = analysis.get('tempo', 120)
        energy_avg = sum(analysis.get('energy_curve', [0])) / len(analysis.get('energy_curve', [1]))
        
        # Genre classification based on tempo and energy
        if 120 <= tempo <= 135 and energy_avg > 0.6:
            genres.append('house')
        if 128 <= tempo <= 140 and energy_avg > 0.7:
            genres.append('electronic')
        if 60 <= tempo <= 90:
            genres.append('chill')
        if tempo > 140:
            genres.append('high_energy')
        if 90 <= tempo <= 110 and energy_avg < 0.5:
            genres.append('ambient')
        
        return genres
    
    def _generate_mood_tags(self, analysis: Dict) -> List[str]:
        """Generate mood tags based on audio analysis"""
        moods = []
        
        energy_avg = sum(analysis.get('energy_curve', [0])) / len(analysis.get('energy_curve', [1]))
        tempo = analysis.get('tempo', 120)
        
        # Energy-based moods
        if energy_avg > 0.8:
            moods.extend(['energetic', 'uplifting', 'party'])
        elif energy_avg > 0.6:
            moods.extend(['upbeat', 'positive'])
        elif energy_avg > 0.4:
            moods.extend(['moderate', 'balanced'])
        else:
            moods.extend(['calm', 'relaxed', 'chill'])
        
        # Tempo-based moods
        if tempo > 140:
            moods.append('fast')
        elif tempo < 80:
            moods.append('slow')
        
        # Key-based moods (simplified)
        key = analysis.get('key', '')
        if 'minor' in key.lower():
            moods.extend(['melancholic', 'emotional'])
        elif 'major' in key.lower():
            moods.extend(['happy', 'bright'])
        
        return list(set(moods))  # Remove duplicates
    
    def batch_fetch_tracks(self, track_queries: List[str], max_workers: int = 3) -> List[Dict]:
        """Fetch multiple tracks in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_query = {
                executor.submit(self.fetch_and_prepare_track, query): query 
                for query in track_queries
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    else:
                        print(f"❌ Failed to fetch: {query}")
                except Exception as e:
                    print(f"❌ Error with {query}: {e}")
        
        return results
    
    def get_local_tracks_metadata(self) -> List[Dict]:
        """Get metadata for all local tracks"""
        metadata_list = []
        
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.enhanced_metadata.json'):
                metadata_path = os.path.join(self.output_dir, filename)
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        if os.path.exists(metadata['file_path']):
                            metadata_list.append(metadata)
                except Exception as e:
                    print(f"⚠️ Error loading metadata from {filename}: {e}")
        
        return metadata_list