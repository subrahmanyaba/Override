# agent/adk_base.py
class Tool:
    def run(self, *args, **kwargs):
        raise NotImplementedError("Tool must implement the run() method.")

class Agent:
    def __init__(self, tools: list):
        self.tools = {tool.__class__.__name__: tool for tool in tools}

    def run(self, plan: dict):
        raise NotImplementedError("Agent must implement the run() method.")
