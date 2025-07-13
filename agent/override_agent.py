from agent.adk_base import Agent
from agent.tools.mix_planner_tool import MixPlannerTool
from agent.tools.auto_mixer_tool import AutoMixerTool
from agent.tools.visual_gen_tool import VisualGenTool

class OverrideAgent(Agent):
    def __init__(self):
        super().__init__(
            tools=[
                MixPlannerTool(),
                AutoMixerTool(),
                VisualGenTool()
            ],
            llm="gemini-2.0-pro"
        )
