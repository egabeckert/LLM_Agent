import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Footer, RichLog, Input, Static, Button, Label
from textual.containers import Vertical, Horizontal, Middle
from textual.screen import ModalScreen
from textual.events import Click
from dotenv import load_dotenv

from gui.agent_logic import run_agent
from utils.conversation_memory import load_memory, save_memory


ASCII_BANNER = """\
  ██████╗██╗  ██╗██╗   ██╗██████╗ ███╗   ██╗███████╗██╗     ██╗██╗   ██╗███████╗
 ██╔════╝██║  ██║██║   ██║██╔══██╗████╗  ██║██╔════╝██║     ██║██║   ██║██╔════╝
 ██║     ███████║██║   ██║██║  ██║██╔██╗ ██║█████╗  ██║     ██║██║   ██║███████╗
 ██║     ██╔══██║██║   ██║██║  ██║██║╚██╗██║██╔══╝  ██║     ██║██║   ██║╚════██║
 ╚██████╗██║  ██║╚██████╔╝██████╔╝██║ ╚████║███████╗███████╗██║╚██████╔╝███████║
  ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚══════╝\
"""

# Burger renders as three stacked bars; X renders as a close symbol
BURGER_CLOSED = "≡"
BURGER_OPEN   = "✕"


class BurgerIcon(Static):
    """
    Clickable icon extending Static so content-align centering works correctly.
    Shows ≡ when menu is closed, ✕ when open. State driven by the app.
    """

    is_open: reactive[bool] = reactive(False)

    def __init__(self, **kwargs):
        super().__init__(BURGER_CLOSED, **kwargs)

    def watch_is_open(self, value: bool) -> None:
        """Reactive watcher — updates content automatically when state changes."""
        self.update(BURGER_OPEN if value else BURGER_CLOSED)

    def set_open(self, state: bool) -> None:
        self.is_open = state

    def on_click(self) -> None:
        if self.is_open:
            self.app.action_close_menu()
        else:
            self.app.action_open_menu()


class MenuModal(ModalScreen):
    """Burger menu overlay — dimmed background, click-outside to close."""

    BINDINGS = [("escape", "dismiss", "Close")]

    def compose(self) -> ComposeResult:
        with Vertical(id="menu_dialog"):
            yield Label("Menu", id="menu_title")
            yield Button("🗑  Clear History", id="menu_clear",      variant="default")
            yield Button("📸  Screenshot",    id="menu_screenshot", variant="default")
            yield Button("✕  Quit",          id="menu_quit",       variant="error")

    def on_click(self, event: Click) -> None:
        if self.get_widget_at(event.screen_x, event.screen_y)[0] is self:
            self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id)


class ChudneliusTUI(App):
    """A Textual TUI for the Chudnelius agent."""

    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("m", "open_menu",     "Menu"),
        ("c", "clear_history", "Clear"),
        ("s", "screenshot",    "Screenshot"),
        ("q", "quit",          "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.messages: list[dict] = load_memory()
        load_dotenv()

    def compose(self) -> ComposeResult:
        yield Static(ASCII_BANNER, id="app_banner")
        with Horizontal(id="status_bar"):
            yield BurgerIcon(id="burger_btn")
            with Middle(id="status_middle"):
                yield Static("● Idle", id="agent_status")
        with Vertical(id="main_layout"):
            yield RichLog(id="chat_history_display", markup=True, wrap=True)
            yield Input(placeholder="Ask Chudnelius...", id="user_input_field")
        yield Footer()

    def on_mount(self) -> None:
        if self.messages:
            chat_history = self.query_one("#chat_history_display", RichLog)
            chat_history.write("[dim]── Restored previous session ──[/dim]")
            for msg in self.messages:
                role = msg.get("role")
                content = msg.get("content")
                if not content:
                    continue
                if role == "user":
                    chat_history.write(f"[bold green]You:[/bold green] {content}")
                elif role == "assistant":
                    chat_history.write(f"[bold orange1]Agent:[/bold orange1] {content}")
        self.query_one("#user_input_field", Input).focus()

    def update_agent_status(self, status: str) -> None:
        indicator = "◌" if status != "Idle" else "●"
        self.query_one("#agent_status", Static).update(f"{indicator} {status}")

    # ── Menu ──────────────────────────────────────────────────────────────────

    def _burger(self) -> BurgerIcon:
        return self.query_one("#burger_btn", BurgerIcon)

    def action_open_menu(self) -> None:
        self._burger().set_open(True)

        def handle_choice(choice: str | None) -> None:
            self._burger().set_open(False)
            if choice == "menu_clear":
                self.action_clear_history()
            elif choice == "menu_screenshot":
                self.action_screenshot()
            elif choice == "menu_quit":
                self.action_quit()

        self.push_screen(MenuModal(), handle_choice)

    def action_close_menu(self) -> None:
        """Called when the burger is clicked while the menu is open."""
        self._burger().set_open(False)
        self.pop_screen()

    # ── Actions ───────────────────────────────────────────────────────────────

    def action_clear_history(self) -> None:
        self.messages.clear()
        save_memory(self.messages)
        self.query_one("#chat_history_display", RichLog).clear()

    def action_screenshot(self) -> None:
        path = self.save_screenshot()
        self.query_one("#chat_history_display", RichLog).write(
            f"[dim]── Screenshot saved: {path} ──[/dim]"
        )

    def action_quit(self) -> None:
        save_memory(self.messages)
        self.exit()

    # ── Input ─────────────────────────────────────────────────────────────────

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        user_message_text = message.value
        if not user_message_text.strip():
            return

        chat_history = self.query_one("#chat_history_display", RichLog)
        user_input_field = self.query_one("#user_input_field", Input)

        chat_history.write(f"[bold green]You:[/bold green] {user_message_text}")
        user_input_field.value = ""
        user_input_field.disabled = True

        self.messages.append({"role": "user", "content": user_message_text})

        try:
            await run_agent(self.messages, chat_history, self.update_agent_status)
        except Exception as e:
            chat_history.write(f"[bold red]Error:[/bold red] {e}")
        finally:
            save_memory(self.messages)
            self.update_agent_status("Idle")
            user_input_field.disabled = False
            user_input_field.focus()


if __name__ == "__main__":
    app = ChudneliusTUI()
    app.run()