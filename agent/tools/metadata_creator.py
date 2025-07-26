# tools/metadata_creator.py

import os
import pdb
import librosa
import json
from mutagen.mp3 import MP3

def create_metadata_for_track(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    print(f"🔍 Creating metadata for: {file_path}")

    try:
        # Load audio using librosa
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beats, sr=sr)

        # Load bitrate and audio info using mutagen
        audio = MP3(file_path)
        bitrate = audio.info.bitrate

        metadata = {
            "filename": os.path.basename(file_path),
            "duration_sec": round(float(duration), 2),
            "tempo_bpm": round(float(tempo), 2),
            "beats": beat_times.tolist(),
            "bitrate": bitrate,
            "sampling_rate": sr
        }

        # Save metadata JSON next to the audio file
        meta_path = file_path.replace(".mp3", ".meta.json")
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Metadata saved to: {meta_path}")
        return metadata

    except Exception as e:
        print(f"❌ Failed to create metadata for {file_path}: {e}")
        return None
