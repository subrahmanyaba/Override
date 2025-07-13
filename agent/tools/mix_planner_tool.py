from agent.adk_base import Tool
from vertexai.generative_models import GenerativeModel

class MixPlannerTool(Tool):
    def run(self, prompt: str) -> dict:
        model = GenerativeModel("gemini-2.0-pro")
        system_prompt = """
        You are an emotion-aware music planner.
        Given a user's current feeling and desired mood, generate:
        {
          "current_emotion": "...",
          "target_emotion": "...",
          "mood_curve": [...],
          "music_suggestions": [...],
          "visual_style": {...}
        }
        """
        response = model.generate_content(system_prompt + prompt)
        return response.text  # or parsed JSON
