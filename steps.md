# TUI Agent Project Planning Steps

This document outlines the initial steps for building a Textual TUI for an agent.

## Phase 1: Setup and Basic Structure

1.  **Install Textual**: Ensure Textual is installed (`pip install textual`).
2.  **Create `gui/app.py`**: Set up a basic Textual application with a simple layout (e.g., a header, a content area, and an input field).
3.  **Run the basic app**: Verify that the Textual application runs without errors.
4.  **Define core components**: Identify the main visual components needed for the agent TUI (e.g., chat history display, agent status, user input, tool output).

## Phase 2: UI Design and Layout

1.  **Design the main screen**:
    *   **Header**: Display agent name, status (e.g., "Thinking...", "Waiting for input").
    *   **Chat History/Output Area**: A scrollable area to display agent responses, user inputs, and tool outputs.
    *   **Input Field**: A multiline input box for the user to type commands or messages.
    *   **Status Bar/Footer**: Display system messages, current mode, or shortcuts.
2.  **Implement Textual Widgets**: Use appropriate Textual widgets for each component (e.g., `Header`, `Footer`, `TextArea`, `RichLog` or `ListView` for history).
3.  **Layout Management**: Use Textual's layout features (e.g., `Vertical`, `Horizontal`, `Grid`) to arrange widgets effectively.

## Phase 3: Interaction and Agent Integration

1.  **Handle User Input**:
    *   Capture input from the `TextArea` when the user presses Enter.
    *   Send the input to the agent backend (this will require defining an interface for the agent).
2.  **Display Agent Output**:
    *   Receive responses from the agent.
    *   Update the chat history/output area with agent messages, tool calls, and tool results.
    *   Consider different styling for user input, agent responses, and tool outputs.
3.  **Agent Status Updates**: Update the header or status bar to reflect the agent's current state (e.g., "Processing...", "Tool Executing...", "Idle").
4.  **Error Handling**: Display errors gracefully within the TUI.

## Phase 4: Advanced Features (Optional)

1.  **Command Palette**: Implement a command palette for quick actions.
2.  **Theming**: Allow users to switch between different themes.
3.  **Configuration**: Load agent configuration from a file.
4.  **Tool Visualization**: If the agent uses tools, consider how to visually represent tool usage and output.

## Relevant Files for `gui` folder:

*   `app.py`: The main Textual application file.
*   `widgets.py` (optional): Custom Textual widgets if needed.
*   `styles.css` (optional): Textual CSS for styling the application.
*   `__init__.py`: To make `gui` a Python package.
