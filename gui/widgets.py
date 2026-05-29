"""
gui/widgets.py

Custom Textual widgets and modal screens used by the TUI.
Kept separate from app.py so the app shell stays clean.
"""

from textual.reactive import reactive
from textual.widgets import Static, Button, Label
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.events import Click


ASCII_BANNER = """\
  ██████╗██╗  ██╗██╗   ██╗██████╗ ███╗   ██╗███████╗██╗     ██╗██╗   ██╗███████╗
 ██╔════╝██║  ██║██║   ██║██╔══██╗████╗  ██║██╔════╝██║     ██║██║   ██║██╔════╝
 ██║     ███████║██║   ██║██║  ██║██╔██╗ ██║█████╗  ██║     ██║██║   ██║███████╗
 ██║     ██╔══██║██║   ██║██║  ██║██║╚██╗██║██╔══╝  ██║     ██║██║   ██║╚════██║
 ╚██████╗██║  ██║╚██████╔╝██████╔╝██║ ╚████║███████╗███████╗██║╚██████╔╝███████║
  ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚══════╝\
"""

BURGER_CLOSED = "≡"
BURGER_OPEN   = "✕"


class BurgerIcon(Static):
    """
    Clickable icon that toggles between ≡ (closed) and ✕ (open).
    Extends Static so content-align centering works correctly.
    State is driven by the app; the icon only reflects and fires actions.
    """

    is_open: reactive[bool] = reactive(False)

    def __init__(self, **kwargs):
        super().__init__(BURGER_CLOSED, **kwargs)

    def watch_is_open(self, value: bool) -> None:
        self.update(BURGER_OPEN if value else BURGER_CLOSED)

    def set_open(self, state: bool) -> None:
        self.is_open = state

    def on_click(self) -> None:
        if self.is_open:
            self.app.action_close_menu()
        else:
            self.app.action_open_menu()


class MenuModal(ModalScreen):
    """
    Burger menu overlay.
    Dimmed background, click-outside or Escape to close.
    Returns the button id of the chosen action, or None if dismissed.
    """

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
