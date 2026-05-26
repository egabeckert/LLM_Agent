
import os
import sys
import subprocess

def display_splash_screen():
    splash = """
   ________  ____  ______  _   __________    ______  _______    
  / ____/ / / / / / / __ \/ | / / ____/ /   /  _/ / / / ___/    
 / /   / /_/ / / / / / / /  |/ / __/ / /    / // / / /\__ \     
/ /___/ __  / /_/ / /_/ / /|  / /___/ /____/ // /_/ /___/ /     
\____/_/ /_/\____/_____/_/ |_/_____/_____/___/\____//____/                                                                    
Welcome to Chudnelius CLI Agent!
"""
    print(splash)

def run_agent(question=None):
    display_splash_screen()
    
    if question is None:
        user_question = input("What can I help you with today? ")
    else:
        user_question = question
    
    # Ensure the user question is properly quoted for the command line
    # This handles cases where the question might contain spaces or special characters
    # For subprocess.run, it's better to pass arguments as a list
    command_args = ["uv", "run", "main.py", user_question]
    
    print(f"Running command: {' '.join(command_args)}")
    
    try:
        result = subprocess.run(command_args, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running agent: {e}", file=sys.stderr)
        print(e.stdout, file=sys.stderr)
        print(e.stderr, file=sys.stderr)
    except FileNotFoundError:
        print("Error: 'uv' command not found. Please ensure uv is installed and in your PATH.", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_agent(question=" ".join(sys.argv[1:]))
    else:
        run_agent()
