import os
import argparse
import sys
import json
from dotenv import load_dotenv
from agent.generate_content import generate_content
from agent.call_function import call_function

def _handle_tool_calls(tool_calls, messages, verbose):
    """Handles tool calls and appends their outputs to messages."""
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Trimmed down call reporting to only display tool calls
        print(f" - Calling function: {function_name}")
        
        tool_output = call_function(function_name, function_args, verbose)
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(tool_output),
            }
        )

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    messages: list[dict] = [
         {"role": "user", "content": args.user_prompt}
    ]

    for _ in range(20):
        message = generate_content(messages, args.verbose)

        # 1. Always append the assistant message to history as a clean dict
        messages.append(message.model_dump(exclude_none=True))

        # 2. If the assistant wants to call tools, do that and continue the loop
        if message.tool_calls:
            _handle_tool_calls(message.tool_calls, messages, args.verbose)
        
        # 3. If there are no tool calls, check for text content
        elif message.content is not None:
            print("Final response:")
            print(message.content)
            return
        
        # 4. Fallback if the model returns nothing at all
        else:
            print("The agent returned an empty response or an unexpected message structure.")
            print(f"Message object: {message.model_dump_json(indent=2)}") # Add this line for debugging
            return

    print("Maximum iterations reached")
    sys.exit(1)

if __name__ == "__main__":
    main()
