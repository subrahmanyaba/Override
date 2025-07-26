import pdb
from agent.adk_base import Tool
from core.visual_engine import generate_visuals_from_mood

class VisualGenTool(Tool):
    def run(self, mood_curve):
        return generate_visuals_from_mood(mood_curve)
