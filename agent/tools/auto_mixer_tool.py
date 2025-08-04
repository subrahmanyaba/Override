from agent.adk_base import Tool
from core.intelligent_auto_mixer import IntelligentAutoMixer

class AutoMixerTool(Tool):
    def __init__(self):
        self.mixer = IntelligentAutoMixer()
    
    def run(self, track_a_path, track_b_path, mood_context):
        return self.mixer.mix_tracks_intelligent(
            track_a_path, track_b_path, mood_context
        )
