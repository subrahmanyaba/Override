import subprocess
import json

class EmotionPlanner:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name

    def plan(self, user_prompt):
        system_prompt = """
        You are an emotion-aware music planner AI.

        Given a user's emotional state and how they want to feel,
        create a structured music and visuals plan.

        Respond ONLY in JSON format:
        {
          "current_emotion": "...",
          "target_emotion": "...",
          "mood_curve": ["...", "...", "..."],
          "music_suggestions": [
            {
              "title": "...",
              "genre": "...",
              "tempo": "...",
              "transition_type": "...",
              "vibe_description": "..."
            }
          ],
          "visual_style": {
            "color_palette": ["#...", "#..."],
            "motion_type": "...",
            "intensity": "low | medium | high"
          }
        }
        """

        full_prompt = f"{system_prompt}\nUser: {user_prompt}"
        result = subprocess.run(
            ["ollama", "run", self.model_name],
            input=full_prompt.encode(),
            stdout=subprocess.PIPE
        )

        # Try parsing JSON from output
        output = result.stdout.decode()
        json_start = output.find("{")
        json_part = output[json_start:]

        try:
            return json.loads(json_part)
        except Exception as e:
            print("[Error] Couldn't parse JSON:", e)
            return {"error": "LLM failed to parse."}
