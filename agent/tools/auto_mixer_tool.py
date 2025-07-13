from agent.adk_base import Tool
from core.auto_mixer import AutoMixer

class AutoMixerTool(Tool):
    def run(self, track_a_path, track_b_path, mood_context):
        mixer = AutoMixer(track_a_path, track_b_path)
        return mixer.mix_tracks()  # or pass mood context to influence it
