# STREAMING.md

## Analysis of Current Implementation

### Backend/Agent Logic (`agent/generate_content.py`, `agent/call_function.py`, and `main.py` for CLI)

*   The core agent logic resides in `agent/generate_content.py` (for LLM interaction) and `agent/call_function.py` (for tool execution).
*   `main.py` provides a command-line interface that uses these agent functions.
*   Responses from `generate_content` are currently returned as a complete `Message` object, containing the full content or tool calls. There is no inherent streaming mechanism at this layer.
*   Tool calls are handled synchronously, and their outputs are appended to the message history before the next `generate_content` call.

### Frontend (TUI) (`gui/app.py`)

*   The application uses the `Textual` TUI framework.
*   The `RichLog` widget (`id="chat_history_display"`) is used to display all conversation history, including user input, agent responses, and tool call information.
*   Agent responses (`agent_response.content`) are written to the `RichLog` *after* the entire `generate_content` call has completed and the full response is available. This confirms the "response displayed all at once" behavior.
*   Tool usage notices are already being written to the `RichLog` within the `_handle_tool_calls` method:
    *   `chat_history.write(f" - Calling function: {function_name}")`
    *   `chat_history.write(f"[bold yellow]Tool Output:[/bold yellow] {tool_output}")`
*   **Scrolling Issue**: The `RichLog` widget is expected to handle vertical scrolling automatically when content overflows. The observation of "horizontal scroll, but not vertical scroll" suggests a potential misconfiguration of the `RichLog` or its parent container, or perhaps very long lines preventing proper wrapping and thus not triggering vertical scroll as expected. Horizontal scroll might be due to `RichLog`'s default behavior for long lines or the terminal's handling.

## Detailed Plan for New Features

### 1. Implement Answer Streaming

The goal is to display the agent's response word-by-word or token-by-token as it's generated, rather than waiting for the full response.

**Roadmap:**

*   **Step 1: Modify `generate_content` for Streaming (Agent Layer)**
    *   **Goal**: Change `agent.generate_content.generate_content` (or the underlying LLM call within it) to return an *iterable* or *asynchronous generator* that yields chunks of the response content.
    *   **Details**:
        *   If the LLM API supports streaming (e.g., `model.generate_content(..., stream=True)` in Google Gemini API), utilize that feature.
        *   The `generate_content` function should then yield `Message` objects (or a simplified structure) containing partial content.
        *   Handle cases where the streamed response might include tool calls mid-stream (though typically tool calls are at the end of a turn or before content).
        *   **Verification**: Create a simple test script that calls the modified `generate_content` and iterates over its output, printing each chunk to confirm streaming behavior.

*   **Step 2: Update `ChudneliusTUI` to Consume Streamed Content (Frontend Layer)**
    *   **Goal**: Modify the `on_input_submitted` method in `gui/app.py` to asynchronously iterate over the streamed response from `generate_content` and update the `RichLog` incrementally.
    *   **Details**:
        *   Change the call `agent_response = generate_content(...)` to `async for chunk in generate_content(...)`.
        *   Inside the loop, append each `chunk.content` to the `RichLog`. The `RichLog` has an `write` method, but for continuous appending, `RichLog.write` might create new lines. We might need to use `RichLog.log` or a custom method to append to the *current* line until a newline character or the end of the stream.
        *   Consider using a temporary buffer or a dedicated `Textual` widget for the *current* streaming response, then moving it to `RichLog` once complete. A simpler approach might be to update the last line of the `RichLog` directly.
        *   Handle `tool_calls` within the stream: if a chunk indicates tool calls, process them immediately.
        *   **Verification**: Run the TUI, submit a prompt, and observe if the agent's response appears character-by-character or word-by-word.

### 2. Implement Vertical Scroll

The `RichLog` widget *should* provide vertical scrolling. The current issue suggests a potential layout or configuration problem.

**Roadmap:**

*   **Step 1: Inspect `RichLog` and Container Configuration**
    *   **Goal**: Verify that the `RichLog` is correctly configured to allow vertical scrolling and that its parent container (`Vertical(id="main_layout")`) is not inadvertently restricting its height.
    *   **Details**:
        *   Review `gui/app.py`'s `compose` method. The `RichLog` is inside a `Vertical` container. `Vertical` containers by default try to give children their preferred height.
        *   Ensure the `RichLog` has `height: 1fr` or `height: auto` (or similar Textual CSS) to allow it to expand and trigger scrolling when content overflows.
        *   Check if any explicit `height` or `max-height` is set on `chat_history_display` or `main_layout` that might be preventing the `RichLog` from growing and thus not activating its scrollbars.
        *   **Hypothesis**: The `RichLog` might be getting a fixed height, or its content is not wrapping, leading to horizontal scroll dominating.
        *   **Verification**: Temporarily add a large amount of dummy text to the `RichLog` on startup to see if vertical scrollbars appear.

*   **Step 2: Ensure Text Wrapping**
    *   **Goal**: Confirm that long lines of text within the `RichLog` are wrapping correctly to prevent excessive horizontal scrolling and encourage vertical scrolling.
    *   **Details**:
        *   `RichLog` typically handles wrapping. If not, investigate Textual CSS properties like `word-wrap` or `overflow-wrap` if available for `RichLog` or its content.
        *   The `RichLog` widget itself has a `wrap` property that can be set to `True`. Ensure this is enabled if it's not by default.
        *   **Verification**: Input a very long, single-line message and observe if it wraps within the terminal width.

### 3. Implement Tool Usage Notices

The current implementation already prints tool usage information to the `RichLog`. The goal is to ensure these notices are clearly visible and potentially integrated into the streaming experience.

**Roadmap:**

*   **Step 1: Enhance Tool Call Display (Frontend)**
    *   **Goal**: Make tool usage notices more prominent and distinct in the `RichLog`.
    *   **Details**:
        *   In `_handle_tool_calls` in `gui/app.py`, ensure the `chat_history.write` calls for tool usage and output use distinct styling (e.g., different colors, bolding, or even a separate "status" line if desired). The current `[bold yellow]` is a good start.
        *   Consider adding a timestamp or a clear separator before/after tool calls for better readability.
        *   **Integration with Streaming**: If the agent streams content, ensure tool call notices are inserted into the stream at the correct logical points (i.e., before the tool is called, and after its output is received). This might involve yielding special "tool_call_start" and "tool_call_end" messages from `generate_content` if the agent logic is modified to stream.
        *   **Verification**: Run the TUI, trigger a tool call, and visually confirm that the tool usage and output messages are clearly distinguishable from regular chat messages.

*   **Step 2: (Optional) Dedicated Status Area for Tools**
    *   **Goal**: If more complex tool interaction feedback is needed, consider a dedicated area.
    *   **Details**:
        *   Add another `Textual` widget (e.g., a `Label` or another `RichLog`) to the `compose` method specifically for "Agent Status" or "Tool Activity."
        *   Update this widget with tool call information as it happens, potentially clearing it once the tool interaction is complete.
        *   This would separate tool notices from the main chat history, making the chat log cleaner.
        *   **Verification**: Observe if tool activity is reflected in the new status area.
