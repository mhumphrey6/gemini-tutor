import sys
import json
import time
import argparse
from tutor_core import TutorSession, ConfigManager

def load_roadmap():
    try:
        with open('curriculum.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def print_roadmap(roadmap):
    if not roadmap:
        print("Roadmap not found.")
        return
    
    print("\n--- LEARNING ROADMAP ---")
    for phase in roadmap.get('roadmap', []):
        print(f"\n[{phase['phase']}]")
        for topic in phase['topics']:
            print(f"  - {topic}")
    print("\n------------------------")

def main():
    parser = argparse.ArgumentParser(description="Gemini Tutor AI")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode (shows latency and system logs)")
    args = parser.parse_args()

    print("--- GEMINI TUTOR: AI & STATISTICS ---")
    if args.debug:
        print("[DEBUG MODE ENABLED]")
    
    config = ConfigManager()
    if not config.api_key:
        print("API Key not found in API_KEY.txt. Please add it.")
        input("Press Enter to exit...")
        return

    session = TutorSession(api_key=config.api_key, debug=args.debug)
    
    while True:
        print("\nMAIN MENU")
        print("1. Start/Resume Session")
        print("2. View Roadmap")
        print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            project = input("Enter Project Name (or press Enter for 'General'): ").strip()
            if not project: project = "General"
            
            print(session.start_session(project_name=project))
            print("Type 'quit' or 'menu' to return to main menu.\n")
            
            while True:
                user_input = input(f"\n[{project}] You: ")
                if user_input.lower() in ['quit', 'exit', 'menu']:
                    break
                
                try:
                    # Show a "thinking" indicator (optional, but nice)
                    if args.debug:
                        print("Tutor is thinking...", end="\r")
                    
                    start_time = time.perf_counter()
                    response = session.send_message(user_input)
                    duration = time.perf_counter() - start_time
                    
                    print(f"\nTutor: {response}")
                    
                    if args.debug:
                        print(f"   [Latency: {duration:.2f}s]")
                    
                    # Log in background
                    session.log_async(user_input, response)
                    
                except Exception as e:
                    print(f"\nError: {e}")
        
        elif choice == '2':
            roadmap = load_roadmap()
            print_roadmap(roadmap)
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
