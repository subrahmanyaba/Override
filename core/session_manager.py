# core/session_manager.py
import random
from gemini_client import get_emotional_plan

class SessionManager:
    def __init__(self, user_prompt):
        self.user_prompt = user_prompt
        self.plan = get_emotional_plan(user_prompt)
        self.track_queue = self.plan.get("music_suggestions", [])
        self.mood_curve = self.plan.get("mood_curve", [])
        self.visual_style = self.plan.get("visual_style", {})
        self.session_id = random.randint(100000, 999999)

    def next_track_pair(self):
        if len(self.track_queue) < 2:
            self.refresh_plan()
        return self.track_queue.pop(0), self.track_queue.pop(0)

    def refresh_plan(self):
        print("🌀 Refreshing plan from Gemini...")
        self.plan = get_emotional_plan(self.user_prompt)
        self.track_queue += self.plan.get("music_suggestions", [])
        self.mood_curve = self.plan.get("mood_curve", [])
        self.visual_style = self.plan.get("visual_style", {})

    def update_prompt(self, new_prompt):
        print(f"🔄 Updating session prompt to: {new_prompt}")
        self.user_prompt = new_prompt
        self.refresh_plan()

    def get_visual_mood(self):
        return self.mood_curve

    def get_session_id(self):
        return self.session_id
