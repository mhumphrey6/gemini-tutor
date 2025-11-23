import sys
import json
import time
import argparse
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from tutor_core import TutorSession, ConfigManager
from user_profile import UserProfile

console = Console()

def load_roadmap():
    try:
        with open('curriculum.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def print_roadmap(roadmap):
    if not roadmap:
        console.print("[bold red]Roadmap not found.[/bold red]")
        return
    
    console.print("\n[bold cyan]--- LEARNING ROADMAP ---[/bold cyan]")
    for phase in roadmap.get('roadmap', []):
        console.print(f"\n[bold yellow][{phase['phase']}][/bold yellow]")
        for topic in phase['topics']:
            console.print(f"  - {topic}")
    console.print("\n[bold cyan]------------------------[/bold cyan]")

def main():
    parser = argparse.ArgumentParser(description="Gemini Tutor AI")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode (shows latency and system logs)")
    args = parser.parse_args()

    console.print(Panel.fit("[bold blue]GEMINI TUTOR: AI & STATISTICS[/bold blue]", border_style="blue"))
    if args.debug:
        console.print("[bold red][DEBUG MODE ENABLED][/bold red]")
    
    config = ConfigManager()
    if not config.api_key:
        console.print("[bold red]API Key not found in API_KEY.txt. Please add it.[/bold red]")
        input("Press Enter to exit...")
        return

    session = TutorSession(api_key=config.api_key, debug=args.debug)
    user_profile = UserProfile()

    if not user_profile.name:
        console.print("\n[bold green]Welcome! I don't believe we've met.[/bold green]")
        name = input("What should I call you? ").strip()
        user_profile.name = name
    
    console.print(f"\n[bold green]Welcome back, {user_profile.name}![/bold green]")
    
    while True:
        console.print("\n[bold green]MAIN MENU[/bold green]")
        console.print("1. Start/Resume Session")
        console.print("2. View Roadmap")
        console.print("3. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            default_project = user_profile.last_project or "General"
            project = input(f"Enter Project Name (default: '{default_project}'): ").strip()
            if not project: project = default_project
            
            user_profile.last_project = project
            
            console.print(f"[italic]Starting session for: {project}[/italic]")
            print(session.start_session(project_name=project))
            console.print("Type 'quit' or 'menu' to return to main menu.\n")
            
            while True:
                user_input = input(f"\n[{project}] You: ")
                if user_input.lower() in ['quit', 'exit', 'menu']:
                    console.print("\n[bold yellow]Generating Session Report Card...[/bold yellow]")
                    report = session.generate_report_card()
                    console.print(Panel(Markdown(report), title="Session Summary", border_style="green"))
                    break
                
                try:
                    # Show a "thinking" indicator (optional, but nice)
                    if args.debug:
                        console.print("[dim]Tutor is thinking...[/dim]", end="\r")
                    
                    start_time = time.perf_counter()
                    response = session.send_message(user_input)
                    duration = time.perf_counter() - start_time
                    
                    console.print("\n[bold green]Tutor:[/bold green]")
                    console.print(Markdown(response))
                    
                    if args.debug:
                        console.print(f"   [dim][Latency: {duration:.2f}s][/dim]")
                    
                    # Log in background
                    session.log_async(user_input, response)
                    
                except Exception as e:
                    console.print(f"\n[bold red]Error: {e}[/bold red]")
        
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
