from collections import deque
import logging

logger = logging.getLogger(__name__)

class PlaylistManager:
    def __init__(self, min_unique: int = 20, ban_window: int = 10):
        self.played_songs = deque(maxlen=min_unique)
        self.ban_window = ban_window
        self.banned = deque(maxlen=ban_window)

    def is_allowed(self, song: str) -> bool:
        """Check if song can be played now"""
        return song not in self.banned

    def add_played(self, song: str):
        """Update tracking after playing"""
        self.played_songs.append(song)
        self.banned.append(song)

    def needs_refresh(self) -> bool:
        """Check if we should get new recommendations"""
        return len(self.played_songs) >= self.played_songs.maxlen