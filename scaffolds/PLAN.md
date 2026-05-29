# Code Reorganization Plan for `gui/app.py`

## Current State Analysis

The `gui/app.py` file currently contains the `ChudneliusTUI` class, which encapsulates both the Textual UI components and the core agent interaction logic. This includes methods for handling user input, managing the conversation flow with the agent (calling `generate_content`), processing tool calls, and updating the UI.

## Goal

Reorganize the code to separate the core agent interaction logic from the UI presentation logic. The `ChudneliusTUI` class in `app.py` will primarily manage the UI and orchestrate calls to external functions for agent-specific tasks.

## Proposed Directory Structure

To achieve better separation of concerns, a new directory `gui/agent_logic` will be created to house functions related to the agent's conversational and tool-handling capabilities.

```
gui/
├── app.py
└── agent_logic/
    ├── __init__.py
    ├── tool_handler.py
    └── conversation_manager.py
```

## Proposed File Contents (Conceptual)

### `gui/app.py` (Main Loop and UI)

*   **`ChudneliusTUI` Class**:
    *   Will retain UI-specific methods: `compose`, `action_toggle_dark`, `action_quit`, `update_agent_status`.
    *   The `on_input_submitted` method will be refactored to:
        *   Handle initial user input display.
        *   Call a new function (e.g., `handle_agent_conversation` from `conversation_manager.py`) to process the user's message and get the agent's response.
        *   Update the UI with the agent's response and status based on the results from the `conversation_manager`.
    *   The `_handle_tool_calls` method will be removed, and its logic will be moved to `tool_handler.py`.

### `gui/agent_logic/tool_handler.py`

*   **`handle_tool_calls(messages: list[dict], tool_calls, verbose: bool) -> tuple[list[dict], list[str]]`**:
    *   This function will encapsulate the logic currently in `ChudneliusTUI._handle_tool_calls`.
    *   It will take the current `messages` list, the `tool_calls` object, and a `verbose` flag.
    *   It will call `agent.call_function` for each tool call.
    *   It will return the updated `messages` list (with tool outputs appended) and a list of strings representing log entries to be displayed in the UI.

### `gui/agent_logic/conversation_manager.py`

*   **`handle_agent_conversation(messages: list[dict], user_message_text: str, verbose: bool, update_status_callback) -> tuple[list[dict], list[str]]`**:
    *   This function will encapsulate the core agent interaction loop currently in `ChudneliusTUI.on_input_submitted` (the `for _ in range(20):` loop).
    *   It will take the current `messages` list, the `user_message_text`, a `verbose` flag, and a callback function for updating the agent's status in the UI.
    *   It will append the user's message to `messages`.
    *   It will call `agent.generate_content`.
    *   If `tool_calls` are present, it will call `tool_handler.handle_tool_calls`.
    *   It will append the agent's response (or tool outputs) to `messages`.
    *   It will return the updated `messages` list and a list of strings representing log entries (agent's content, errors, max iterations reached) to be displayed in the UI.

## Step-by-Step Reorganization

1.  **Create `gui/agent_logic` directory**:
    *   `create_directory("gui/agent_logic")`
2.  **Create `gui/agent_logic/__init__.py`**:
    *   `write_file("gui/agent_logic/__init__.py", "")`
3.  **Create `gui/agent_logic/tool_handler.py` (placeholder)**:
    *   `write_file("gui/agent_logic/tool_handler.py", "# Placeholder for tool handling logic")`
4.  **Create `gui/agent_logic/conversation_manager.py` (placeholder)**:
    *   `write_file("gui/agent_logic/conversation_manager.py", "# Placeholder for conversation management logic")`
5.  **Update `gui/app.py`**:
    *   Modify `gui/app.py` to import functions from `gui.agent_logic.tool_handler` and `gui.agent_logic.conversation_manager`.
    *   Move the logic from `_handle_tool_calls` into `tool_handler.py`.
    *   Refactor `on_input_submitted` to call `handle_agent_conversation` and update the UI based on its return values.
    *   Remove the `_handle_tool_calls` method from the `ChudneliusTUI` class.