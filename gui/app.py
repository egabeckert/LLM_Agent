import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Input
from textual.containers import Vertical
from textual.message import Message
import asyncio
import json
from dotenv import load_dotenv

# Import LLM functions
from agent.generate_content import generate_content
from agent.call_function import call_function

class ChudneliusTUI(App):
    """A Textual TUI for the Chudnelius agent."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.messages: list[dict] = []
        load_dotenv() # Load environment variables

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True, id="app_header")
        with Vertical(id="main_layout"):
            yield RichLog(id="chat_history_display")
            yield Input(placeholder="Type your message here...", id="user_input_field")
        yield Footer()

    def update_agent_status(self, status: str) -> None:
        """Update the agent status in the header."""
        header = self.query_one("#app_header", Header)
        header.title = f"Chudnelius Agent - Status: {status}"

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """An action to quit the application."""
        self.exit()

    async def _handle_tool_calls(self, tool_calls, verbose):
        """Handles tool calls and appends their outputs to messages."""
        chat_history = self.query_one("#chat_history_display", RichLog)
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            chat_history.write(f" - Calling function: {function_name}")
            
            tool_output = call_function(function_name, function_args, verbose)
            self.messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_output),
                }
            )
            chat_history.write(f"[bold yellow]Tool Output:[/bold yellow] {tool_output}")


    async def on_input_submitted(self, message: Input.Submitted) -> None:
        """Handle user input when Enter is pressed."""
        user_message_text = message.value
        chat_history = self.query_one("#chat_history_display", RichLog)
        user_input_field = self.query_one("#user_input_field", Input)

        chat_history.write(f"[bold blue]You:[/bold blue] {user_message_text}")
        user_input_field.value = ""

        self.update_agent_status("Thinking...")

        try:
            self.messages.append({"role": "user", "content": user_message_text})

            for _ in range(20): # Max iterations for agent
                agent_response = generate_content(self.messages, verbose=True) # Assuming verbose is always true for now

                self.messages.append(agent_response.model_dump(exclude_none=True))

                if agent_response.tool_calls:
                    await self._handle_tool_calls(agent_response.tool_calls, verbose=True)
                elif agent_response.content is not None:
                    chat_history.write(f"[bold green]Agent:[/bold green] {agent_response.content}")
                    self.update_agent_status("Idle")
                    break
                else:
                    chat_history.write("[bold red]The agent returned an empty response or an unexpected message structure.[/bold red]")
                    self.update_agent_status("Error")
                    break
            else:
                chat_history.write("[bold red]Maximum iterations reached without a final response.[/bold red]")
                self.update_agent_status("Error")


        except Exception as e:
            chat_history.write(f"[bold red]An unexpected error occurred:[/bold red] {e}")
            self.update_agent_status("Error")
        
        self.update_agent_status("Idle")


if __name__ == "__main__":
    app = ChudneliusTUI()
    app.run()
