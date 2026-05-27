
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Input
from textual.containers import VerticalScroll, Horizontal

class AgentTUI(App):
    """A Textual TUI for an agent."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit_app", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with VerticalScroll(id="chat-history"):
            yield RichLog(id="log")
        with Horizontal(id="input-area"):
            yield Input(placeholder="Type your message here...", id="user-input")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#user-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission."""
        user_message = event.value
        if user_message:
            log = self.query_one("#log", RichLog)
            log.write(f"[bold blue]User:[/bold blue] {user_message}")
            event.input.value = "" # Clear the input field

            # Here you would typically send the message to your agent
            # and then display the agent's response.
            # For now, let's simulate an agent response.
            log.write("[bold green]Agent:[/bold green] Thinking...")
            # Simulate agent processing and response
            self.call_after_refresh(self.simulate_agent_response, user_message)

    def simulate_agent_response(self, user_message: str) -> None:
        log = self.query_one("#log", RichLog)
        if "hello" in user_message.lower():
            response = "Hello there! How can I assist you today?"
        elif "time" in user_message.lower():
            import datetime
            response = f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."
        else:
            response = f"You said: '{user_message}'. I'm a simple agent, but I'm learning!"
        log.write(f"[bold green]Agent:[/bold green] {response}")


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit_app(self) -> None:
        """An action to quit the application."""
        self.exit()

if __name__ == "__main__":
    app = AgentTUI()
    app.run()
