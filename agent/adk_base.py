# agent/adk_base.py
class Tool:
    def run(self, *args, **kwargs):
        raise NotImplementedError

class Agent:
    def __init__(self, tools, llm):
        self.tools = tools
        self.llm = llm  # e.g., 'gemini-2.0-pro'

    def run(self, prompt: str):
        # Dumb planner for now: always call MixPlannerTool
        for tool in self.tools:
            if "Planner" in tool.__class__.__name__:
                return tool.run(prompt)
        return "No planner tool found."
