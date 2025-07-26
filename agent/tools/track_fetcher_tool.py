# agent/tools/track_fetcher_tool.py
from agent.adk_base import Tool
from agent.tools.track_fetcher import fetch_and_prepare_track

class TrackFetcherTool(Tool):
    def run(self, youtube_url: str) -> str:
        return fetch_and_prepare_track(youtube_url)
