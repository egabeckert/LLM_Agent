import os
import argparse
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from generate_content import generate_content

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key is None:
        raise RuntimeError("API Key Not Found. Chudnelius on Standby...")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    client = genai.Client(api_key=api_key)
    messages: list[types.Content] = [
         types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    for _ in range(20):
        final_response = generate_content(client, messages, args.verbose)

        if final_response:
            print("Final response:")
            print(final_response)
            return

    print("Maximum iterations reached")
    sys.exit(1)

                
                
     

if __name__ == "__main__":
    main()
