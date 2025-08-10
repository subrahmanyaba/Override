import yt_dlp
import os
from pathlib import Path
import logging
import yaml  # This was missing
from typing import Optional

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, config_path: str = "config/config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)  # Now yaml is defined
        
        self.download_dir = Path(self.config["youtube"]["download_dir"])
        self.download_dir.mkdir(exist_ok=True)

    def _get_ydl_opts(self) -> dict:
        return {
            "format": self.config["youtube"]["format"],
            "outtmpl": str(self.download_dir / "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }],
            "quiet": True,
        }

    def search_and_download(self, query: str) -> Optional[str]:
        """Search YouTube and download the first result"""
        try:
            with yt_dlp.YoutubeDL(self._get_ydl_opts()) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                if not info["entries"]:
                    return None
                
                downloaded_file = ydl.prepare_filename(info["entries"][0])
                return downloaded_file.replace(".webm", ".mp3").replace(".m4a", ".mp3")
                
        except Exception as e:
            logger.error(f"Failed to download {query}: {e}")
            return None