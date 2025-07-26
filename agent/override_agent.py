# agent/override_agent.py
from agent.adk_base import Agent
from agent.tools.mix_planner_tool import MixPlannerTool
from agent.tools.auto_mixer_tool import AutoMixerTool
from agent.tools.track_fetcher_tool import TrackFetcherTool
from agent.tools.visual_gen_tool import VisualGenTool
from agent.tools.playback_agent import PlaybackAgent
import pdb  # For debugging purposes

class OverrideAgent(Agent):
    def __init__(self):
        super().__init__([
            MixPlannerTool(),
            AutoMixerTool(),
            VisualGenTool(),
            TrackFetcherTool()
        ])
        self.playback_agent = PlaybackAgent()

    def run_mix(self, track_a_path, track_b_path, mood_curve):
        """Mix two tracks with mood-aware crossfade and visuals."""
        print("🎧 Mixing tracks...")
        mix_path = self.tools["AutoMixerTool"].run(track_a_path, track_b_path, mood_curve)

        # print("🎨 Generating visuals...")
        # try:
        #     visuals = self.tools["VisualGenTool"].run(mood_curve)
        # except Exception as e:
        #     print(f"❌ Error generating visuals: {e}")
        #     visuals = None
        # self.tools["VisualGenTool"].run(mood_curve)

        print("🔊 Playing final mix...")
        print(f"Mix saved to: {mix_path}")
        self.playback_agent.play(mix_path)  # ✅ PLAY IN BACKGROUND

        print("✅ Mix, visuals, and playback complete.")
