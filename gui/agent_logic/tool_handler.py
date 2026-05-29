# Placeholder for tool handling logic
import asyncio
import json
from textual.widgets import RichLog
from agent.call_function import call_function


async def handle_tool_calls(tool_calls: list[dict], messages: list[dict], chat_history: RichLog) -> None:
    """
    Execute each tool call, display the result in the chat log,
    and append the tool response to the message history.
    """
    for tool_call in tool_calls:
        function_name = tool_call["function"]["name"]
        tool_id = tool_call.get("id") or f"call_{hash(function_name)}"

        try:
            function_args = json.loads(tool_call["function"]["arguments"])
        except (json.JSONDecodeError, TypeError):
            function_args = {}

        chat_history.write(f" - Calling function: [bold]{function_name}[/bold]")

        # Run blocking tool in a thread so the TUI event loop stays responsive
        tool_output = await asyncio.get_event_loop().run_in_executor(
            None, call_function, function_name, function_args, True
        )

        messages.append(
            {
                "tool_call_id": tool_id,
                "role": "tool",
                "name": function_name,
                "content": str(tool_output),
            }
        )

        chat_history.write(f"[bold yellow]Tool Output:[/bold yellow] {tool_output}")