# Placeholder for conversation management logic
import asyncio
from textual.widgets import RichLog
from agent.generate_content import generate_content
from gui.agent_logic.tool_handler import handle_tool_calls

MAX_ITERATIONS = 20


async def run_agent(messages: list[dict], chat_history: RichLog, update_status) -> None:
    """
    Core agentic loop. Streams text live into the RichLog, handles tool calls,
    and drives the conversation until the model returns a final text response.

    Args:
        messages:       Full conversation history. Mutated in place as the loop runs.
        chat_history:   The RichLog widget to stream output into.
        update_status:  Callable(str) — updates the header status label in the TUI.
    """
    for _ in range(MAX_ITERATIONS):
        update_status("Thinking...")

        assistant_message = None
        stream_buffer = []

        def on_chunk(text: str) -> None:
            """
            Receives each streamed text fragment from the generator thread.
            Buffers chunks and flushes complete lines (split on newline) to the
            RichLog via call_from_thread, so wrap=True can work on whole lines.
            """
            stream_buffer.append(text)
            combined = "".join(stream_buffer)

            lines = combined.split("\n")
            for line in lines[:-1]:
                if line:
                    chat_history.app.call_from_thread(
                        chat_history.write,
                        f"[bold orange1]Agent:[/bold orange1] {line}",
                    )
                else:
                    chat_history.app.call_from_thread(chat_history.write, "")

            stream_buffer.clear()
            stream_buffer.append(lines[-1])

        def _run_generator() -> dict | None:
            """Consume the blocking generator in a worker thread."""
            final = None
            for event in generate_content(messages, verbose=True, on_chunk=on_chunk):
                if event["type"] == "message":
                    final = event
            return final

        loop = asyncio.get_event_loop()
        assistant_message = await loop.run_in_executor(None, _run_generator)

        # Flush any remaining buffered text after the stream ends
        remainder = "".join(stream_buffer).strip()
        if remainder:
            chat_history.write(f"[bold orange1]Agent:[/bold orange1] {remainder}")

        if assistant_message is None:
            chat_history.write("[bold red]Empty response from agent.[/bold red]")
            return

        # Append to history, stripping internal 'type' key and None values
        messages.append(
            {k: v for k, v in assistant_message.items() if k != "type" and v is not None}
        )

        if assistant_message.get("tool_calls"):
            await handle_tool_calls(assistant_message["tool_calls"], messages, chat_history)
            continue

        if assistant_message.get("content"):
            return  # Text was already streamed live; nothing more to do

        chat_history.write("[bold red]Agent returned an empty or unexpected response.[/bold red]")
        return

    chat_history.write("[bold red]Maximum iterations reached without a final response.[/bold red]")