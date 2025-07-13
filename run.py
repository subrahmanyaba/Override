


# run.py
import time
from core.dj_controller import DJController
from core.visual_engine import visualize_waveform, visualize_spectrogram
from core.auto_mixer import AutoMixer
from core.track_analysis import analyze_track

if __name__ == '__main__':

    # Basic functionality test for DJController and visualizations
    # track_path = "data\\mixed\\mix_output.mp3"  # Replace with your own track

    # print("\nInitializing DJController...")
    # dj = DJController(track_path)
    # dj.load_track()

    # print("Playing track...")
    # dj.play()
    # time.sleep(300)

    # print("Pausing...")
    # dj.pause()
    # time.sleep(2)

    # print("Unpausing...")
    # dj.unpause()
    # time.sleep(5)

    # print("Stopping...")
    # dj.stop()

    # print("\nVisualizing waveform...")
    # visualize_waveform(track_path)

    # print("\nVisualizing spectrogram...")
    # visualize_spectrogram(track_path)

    # Mix tracks (if you have two tracks and their metadata)

    # create metadata for the tracks first
    # print("\nAnalyzing tracks...")
    # analyze_track("data/tracks/empty.mp3")  # Replace with your own track
    # analyze_track("data/tracks/swedish.mp3")  # Replace with your own track

    # Automixer_obj = AutoMixer(
    #     track_a_path="data/tracks/empty.mp3",  # Replace with your own track A
    #     track_b_path="data/tracks/swedish.mp3"   # Replace with your own track B
    # )




    # try:
    #     print("\nMixing tracks...")
    #     Automixer_obj.mix_tracks(output_path="data/mixed/mix_output.mp3")
    # except Exception as e:
    #     print(f"Error during mixing: {e}")

    from agent.override_agent import OverrideAgent

    if __name__ == "__main__":
        agent = OverrideAgent()
        user_prompt = "Today was exhausting. I want to feel inspired and recharged."
        result = agent.run(user_prompt)
        print(result)

    

