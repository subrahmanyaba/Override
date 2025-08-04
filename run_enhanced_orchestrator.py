# run_enhanced_orchestrator.py
import pdb
import time
from core.intelligent_session_manager import IntelligentSessionManager
from agent.enhanced_override_agent import EnhancedOverrideAgent
from core.intelligent_auto_mixer import IntelligentAutoMixer
from concurrent.futures import ThreadPoolExecutor

def print_session_intro():
    """Print a nice intro for the session"""
    print("🎵" + "="*60 + "🎵")
    print("    🤖 INTELLIGENT AGENTIC DJ ORCHESTRATOR 🤖")
    print("         Advanced Emotional Music Mixing")
    print("🎵" + "="*60 + "🎵\n")

def get_user_input_with_validation():
    """Get user input with some basic validation"""
    while True:
        user_prompt = input("📝 How are you feeling today? What do you want to feel like?\n> ").strip()
        
        if len(user_prompt) < 5:
            print("⚠️  Please provide a more detailed description of your mood/goals.")
            continue
        elif len(user_prompt) > 200:
            print("⚠️  Please keep your description under 200 characters.")
            continue
        else:
            return user_prompt

def display_session_stats(session):
    """Display current session statistics"""
    stats = session.get_session_stats()
    
    print("\n📊 SESSION STATISTICS:")
    print(f"   🎵 Tracks played: {stats['tracks_played']}")
    print(f"   😊 Current emotion: {stats['current_emotion']}")
    print(f"   🎯 Target emotion: {stats['target_emotion']}")
    if stats['average_mix_quality'] > 0:
        print(f"   🎛️ Average mix quality: {stats['average_mix_quality']:.1f}/10")
    
    # Energy progression
    energy_prog = stats.get('energy_progression', {})
    if energy_prog.get('progression') != 'insufficient_data':
        print(f"   ⚡ Energy: {energy_prog['start_energy']} → {energy_prog['current_energy']} ({energy_prog['trend']})")
    
    # Tempo progression
    tempo_prog = stats.get('tempo_progression', {})
    if tempo_prog.get('progression') != 'insufficient_data':
        print(f"   🥁 Tempo: {tempo_prog['start_tempo']:.0f} → {tempo_prog['current_tempo']:.0f} BPM")

def get_user_choice():
    """Get user's choice for next action"""
    print("\n💬 What would you like to do?")
    print("   [c] Continue with current mood")
    print("   [m] Change emotional direction")
    print("   [s] Show session statistics")
    print("   [r] Rate last mix")
    print("   [e] End session")
    
    while True:
        choice = input("\n> ").strip().lower()
        if choice in ['c', 'm', 's', 'r', 'e']:
            return choice
        print("⚠️ Please enter c, m, s, r, or e")

def rate_last_mix(session):
    """Allow user to rate the last mix"""
    print("\n⭐ How was that last mix?")
    print("   1 - Terrible")
    print("   2 - Poor") 
    print("   3 - Okay")
    print("   4 - Good")
    print("   5 - Excellent")
    
    try:
        rating = int(input("\nRating (1-5): ").strip())
        if 1 <= rating <= 5:
            feedback = input("Any specific feedback? (optional): ").strip()
            session.record_user_feedback(feedback or "Rating only", rating)
            print(f"✅ Thanks! Recorded rating: {rating}/5")
        else:
            print("⚠️ Please enter a number between 1 and 5")
    except ValueError:
        print("⚠️ Please enter a valid number")

def main():
    """Enhanced main orchestrator loop"""
    
    print_session_intro()
    
    # Get user input
    user_prompt = get_user_input_with_validation()
    
    # Initialize enhanced components
    print("\n🚀 Initializing intelligent session...")
    session = IntelligentSessionManager(user_prompt)
    agent = EnhancedOverrideAgent()
    mixer = IntelligentAutoMixer()
    
    print(f"🔗 Session ID: {session.get_session_id()}")
    print("🎶 Starting enhanced emotional mix journey...\n")
    
    session_start_time = time.time()
    mix_count = 0
    
    try:
        while True:
            mix_count += 1
            print(f"\n🎵 === MIX #{mix_count} === 🎵")
            
            # Get intelligently selected track pair
            track_a, track_b = session.next_track_pair_intelligent()
            
            if not track_a or not track_b:
                print("❌ Unable to find suitable tracks. Try refreshing or changing your mood.")
                user_choice = get_user_choice()
                if user_choice == 'm':
                    new_prompt = input("📝 New emotional direction:\n> ")
                    session.update_prompt(new_prompt)
                    continue
                elif user_choice == 'e':
                    break
                else:
                    continue
            
            print(f"🎵 Track A: {track_a['title']}")
            print(f"🎵 Track B: {track_b['title']}")
            
            # Show mix compatibility info
            if track_a.get('tempo') and track_b.get('tempo'):
                tempo_diff = abs(track_a['tempo'] - track_b['tempo'])
                print(f"🥁 Tempo: {track_a['tempo']:.0f} → {track_b['tempo']:.0f} BPM (Δ{tempo_diff:.0f})")
            
            if track_a.get('camelot_key') and track_b.get('camelot_key'):
                print(f"🎼 Keys: {track_a['camelot_key']} → {track_b['camelot_key']}")
            
            # Perform intelligent mixing in parallel with visual generation
            print("\n🎛️ Creating intelligent mix...")
            
            with ThreadPoolExecutor() as executor:
                # Submit mixing task
                mix_future = executor.submit(
                    mixer.mix_tracks_intelligent,
                    track_a['file_path'],
                    track_b['file_path'],
                    session.get_visual_mood(),
                    'smooth',  # Can be made dynamic based on mood
                    f"data/mixed/session_{session.get_session_id()}_mix_{mix_count}.mp3"
                )
                
                # Submit visual generation task
                visual_future = executor.submit(
                    agent.tools["VisualGenTool"].run,
                    session.get_visual_mood()
                )
                
                # Wait for mixing to complete
                try:
                    mix_path = mix_future.result(timeout=60)  # 60 second timeout
                    print(f"✅ Mix created: {mix_path}")
                except Exception as e:
                    print(f"❌ Mix creation failed: {e}")
                    mix_path = None
                
                # Wait for visuals (don't block on this)
                try:
                    visual_future.result(timeout=30)
                    print("🎨 Visuals generated")
                except Exception as e:
                    print(f"⚠️ Visual generation issue: {e}")
            
            # Play the mix if successful
            if mix_path:
                print("🔊 Playing mix...")
                try:
                    agent.playback_agent.play(mix_path)
                    print(f"🎵 Now playing: {track_a['title']} → {track_b['title']}")
                except Exception as e:
                    print(f"⚠️ Playback issue: {e}")
            
            # Show session progress
            display_session_stats(session)
            
            # Get user input for next action
            user_choice = get_user_choice()
            
            if user_choice == 'c':
                print("🎵 Continuing with current vibe...")
                continue
            
            elif user_choice == 'm':
                new_prompt = input("📝 New emotional direction:\n> ")
                session.update_prompt(new_prompt)
                print("🔄 Updated emotional direction")
            
            elif user_choice == 's':
                display_session_stats(session)
                continue
            
            elif user_choice == 'r':
                rate_last_mix(session)
                continue
            
            elif user_choice == 'e':
                print("🛑 Ending session...")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Session manually interrupted.")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        pdb.post_mortem()
    
    finally:
        # Session cleanup and summary
        session_duration = time.time() - session_start_time
        
        print(f"\n🎵 SESSION SUMMARY 🎵")
        print(f"⏱️  Duration: {session_duration/60:.1f} minutes")
        print(f"🎵 Tracks mixed: {mix_count}")
        print(f"🎛️  Session ID: {session.get_session_id()}")
        
        # Save session data
        try:
            session_file = session.save_session_data()
            print(f"💾 Session data saved for future improvements")
        except Exception as e:
            print(f"⚠️ Could not save session data: {e}")
        
        print("\n🎵 Thanks for using the Intelligent DJ Orchestrator! 🎵")

if __name__ == "__main__":
    main()