import pdb
from pydub import AudioSegment
import json
import os

class AutoMixer:
    def __init__(self, track_a_path, track_b_path):
        self.track_a_path = track_a_path
        self.track_b_path = track_b_path
        self.meta_a = self.load_metadata(track_a_path)
        self.meta_b = self.load_metadata(track_b_path)

    def load_metadata(self, track_path):
        meta_path = track_path.replace(".mp3", ".meta.json")
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata not found for {track_path}")
        with open(meta_path, "r") as f:
            return json.load(f)

    # Mixes
    def mix_tracks(self, output_path="data/mixed/mix_output.mp3", crossfade_ms=8000):
        print("Loading tracks...")
        track_a = AudioSegment.from_file(self.track_a_path)
        track_b = AudioSegment.from_file(self.track_b_path)

        # Use beat timings to determine where to start track_b
        beat_a = self.meta_a['beats']
        beat_b = self.meta_b['beats']

        if len(beat_a) < 4 or len(beat_b) < 4:
            raise ValueError("Not enough beat data for mixing.")

        # Use last beat from A and align with first beat from B
        time_a_ms = int(beat_a[-4] * 1000)
        time_b_ms = int(beat_b[0] * 1000)

        print(f"Aligning track B at {time_b_ms}ms with end of track A at {time_a_ms}ms")

        # Trim B so it starts on beat
        track_b_aligned = track_b[time_b_ms:]

        # Create mix using crossfade
        part_a = track_a[:time_a_ms]
        part_mix = part_a.append(track_b_aligned, crossfade=crossfade_ms)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        part_mix.export(output_path, format="mp3")
        print(f"Mix saved to: {output_path}")
        return output_path

    def equal_length_blend(self, output_path="data/mixed/equal_blend.mp3"):
        print("Creating full-length blend...")
        track_a = AudioSegment.from_file(self.track_a_path)
        track_b = AudioSegment.from_file(self.track_b_path)

        min_len = min(len(track_a), len(track_b))
        blended = track_a[:min_len].overlay(track_b[:min_len])

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        blended.export(output_path, format="mp3")
        print(f"Blended mix saved to: {output_path}")

    def beat_matched_cut(self, output_path="data/mixed/beat_cut.mp3", cut_after_ms=15000):
        print("Creating beat-matched cut mix...")
        track_a = AudioSegment.from_file(self.track_a_path)
        track_b = AudioSegment.from_file(self.track_b_path)

        start_a = int(self.meta_a['beats'][0] * 1000)
        start_b = int(self.meta_b['beats'][0] * 1000)

        part_a = track_a[start_a:start_a + cut_after_ms]
        part_b = track_b[start_b:]

        mixed = part_a + part_b

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        mixed.export(output_path, format="mp3")
        print(f"Hard-cut mix saved to: {output_path}")
    
    def staggered_intro(self, output_path="data/mixed/staggered_intro.mp3", fade_in_ms=6000):
        print("Creating staggered intro mix...")
        track_a = AudioSegment.from_file(self.track_a_path)
        track_b = AudioSegment.from_file(self.track_b_path)

        intro = track_a[:10000]  # First 10s of A
        overlay = track_b.fade_in(fade_in_ms)

        mixed = intro.overlay(overlay)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        mixed.export(output_path, format="mp3")
        print(f"Staggered intro mix saved to: {output_path}")

