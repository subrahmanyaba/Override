# run_orchestrator.py
import pdb
from core.session_manager import SessionManager
from agent.override_agent import OverrideAgent
from agent.tools.track_fetcher import fetch_and_prepare_track
from concurrent.futures import ThreadPoolExecutor

if __name__ == "__main__":
    user_prompt = input("📝 How are you feeling today? What do you want to feel like?\n> ")

    # Start session
    session = SessionManager(user_prompt)
    agent = OverrideAgent()

    print(f"🔗 Session ID: {session.get_session_id()}")
    print("🎶 Starting emotional mix journey...\n")

    while True:
        try:
            # Get the next track URLs from the emotional planner
            track_a_url, track_b_url = session.next_track_pair()

            print(f"Track A: {track_a_url}")
            print(f"Track B: {track_b_url}")

            # Download + create metadata + get local MP3 paths
            
            with ThreadPoolExecutor() as executor:
                future_a = executor.submit(fetch_and_prepare_track, track_a_url)
                future_b = executor.submit(fetch_and_prepare_track, track_b_url)

            track_a_path = future_a.result()
            track_b_path = future_b.result()

            # 🎧 Run DJ Mixer with actual files
            if track_a_path is not None and track_b_path is not None:
                agent.tools["AutoMixerTool"].run(track_a_path.get('file_path'), track_b_path.get('file_path'), session.get_visual_mood())

            # 🎥 Generate visuals
            agent.tools["VisualGenTool"].run(session.get_visual_mood())

            print(f"\nNow playing: {track_a_path.get('file_path')} → {track_b_path.get('file_path')}\n")

            agent.run_mix(track_a_path.get('file_path'), track_b_path.get('file_path'), session.get_visual_mood())

            # Let user change emotional direction
            user_input = input("💬 Change emotion prompt? (y/n/end): ").strip().lower()
            if user_input == "y":
                new_prompt = input("📝 New emotion prompt:\n> ")
                session.update_prompt(new_prompt)
            elif user_input == "end":
                print("🛑 Ending session.")
                break

        except KeyboardInterrupt:
            print("\n🛑 Session manually interrupted.")
            break

        except Exception as e:
            print(f"❌ Error: {e}")
