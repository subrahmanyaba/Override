# tools/track_fetcher.py
import os
from yt_dlp import YoutubeDL
from agent.tools.metadata_creator import create_metadata_for_track

def fetch_and_prepare_track(query_or_url, output_dir="data/tracks"):
    os.makedirs(output_dir, exist_ok=True)

    # Auto convert plain song name to ytsearch
    if not query_or_url.startswith("http"):
        query_or_url = f"ytsearch1:{query_or_url}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query_or_url, download=True)
            if 'entries' in info:
                info = info['entries'][0]  # for ytsearch1
            title = info.get("title", "unknown")
            file_path = os.path.join(output_dir, f"{title}.mp3")
    except Exception as e:
        print(f"❌ Error fetching track: {e}")
        return None

    # Generate metadata automatically
    create_metadata_for_track(file_path)

    return {
        "file_path": file_path,
        "title": title,
        "duration": info.get("duration"),
        "uploader": info.get("uploader"),
        "webpage_url": info.get("webpage_url"),
    }
