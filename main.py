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
        function_name = tool_call["function"]["name"]
        raw_args = tool_call["function"]["arguments"]
        tool_id = tool_call.get("id") or f"call_{hash(function_name)}"

        try:
            function_args = json.loads(raw_args)
        except (json.JSONDecodeError, TypeError):
            function_args = {}

        if verbose:
            print(f" - Calling function: {function_name}")

        tool_output = call_function(function_name, function_args, verbose)

        messages.append(
            {
                "tool_call_id": tool_id,
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

    messages: list[dict] = [{"role": "user", "content": args.user_prompt}]

    for _ in range(20):
        assistant_message = None

        for event in generate_content(messages, args.verbose):
            if event["type"] == "chunk":
                # Text already printed live inside generate_content; nothing to do here.
                pass
            elif event["type"] == "message":
                assistant_message = event

        if assistant_message is None:
            print("Received empty response from generator.")
            return

        # Append to history (strip type/None values to keep payload clean)
        messages.append(
            {k: v for k, v in assistant_message.items()
             if k != "type" and v is not None}
        )

        # Handle tool calls → loop back to send results to the model
        if assistant_message.get("tool_calls"):
            _handle_tool_calls(assistant_message["tool_calls"], messages, args.verbose)
            continue

        # Text content was already printed live; just exit cleanly
        if assistant_message.get("content"):
            return

        # Fallback
        print("The agent returned an empty or unexpected response.")
        print(json.dumps(assistant_message, indent=2, default=str))
        return

    print("Maximum iterations reached")
    sys.exit(1)


if __name__ == "__main__":
    main()