# run_mixer.py
# this is a script to run the DJ mixer application, which includes initializing the DJ controller, visualizing tracks, and mixing them.

import time
from core.dj_controller import DJController
from core.visual_engine import visualize_waveform, visualize_spectrogram
from core.auto_mixer import AutoMixer
from core.track_analysis import analyze_track
from core.emotion_planner import EmotionPlanner

if __name__ == '__main__':

    # # create metadata for the tracks first
    # print("\nAnalyzing tracks...")
    # analyze_track("data/tracks/empty.mp3")
    # analyze_track("data/tracks/swedish.mp3")

    # Automixer_obj = AutoMixer(
    #     track_a_path="data/tracks/empty.mp3",  # Replace with your own track A
    #     track_b_path="data/tracks/swedish.mp3"   # Replace with your own track B
    # )

    # try:
    #     print("\nMixing tracks...")
    #     Automixer_obj.mix_tracks(output_path="data/mixed/mix_output_empty.mp3")
    #     Automixer_obj.equal_length_blend(output_path="data/mixed/equal_blend_empty.mp3")
    #     Automixer_obj.beat_matched_cut(output_path="data/mixed/beat_cut_empty.mp3")
    #     Automixer_obj.staggered_intro(output_path="data/mixed/staggered_intro_empty.mp3")
    #     print("Mixing completed successfully.")

    # except Exception as e:
    #     print(f"Error during mixing: {e}")
    planner = EmotionPlanner()
    prompt = "Today was stressful and chaotic. I want to feel peaceful and in control."
    plan = planner.plan(prompt)
    print(plan)

