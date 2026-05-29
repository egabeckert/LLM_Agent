import json
import litellm
from agent.prompts import system_prompt
from agent.functions.get_files_info import schema_get_files_info
from agent.functions.write_file import schema_write_file
from agent.functions.run_python_file import schema_run_python_file
from agent.functions.get_file_content import schema_get_file_content
from agent.functions.create_directory import schema_create_directory
from agent.functions.remove_directory import schema_remove_directory
from agent.functions.remove_file import schema_remove_file
from agent.functions.move_file import schema_move_file
 
 
def generate_content(messages, verbose, on_chunk=None):
    """
    Streams a response from the model.
 
    Yields dicts of two shapes:
 
      {"type": "chunk", "content": "<text>"}
          — a live text fragment as it arrives from the stream.
            Useful for word-by-word display in a TUI or terminal.
 
      {"type": "message", "role": "assistant", "content": <str|None>, "tool_calls": <list|None>}
          — emitted exactly once at the end, containing the fully assembled
            assistant message ready to be appended to the message history.
 
    Args:
        messages:  Conversation history (list of dicts).
        verbose:   If True, print debug info for tool calls etc.
        on_chunk:  Optional callback(str) called for every text chunk.
                   Useful when consuming the generator in a thread and you
                   want to push chunks somewhere without inspecting yields
                   (e.g. call_from_thread in the TUI).
    """
    full_messages = [{"role": "system", "content": system_prompt}] + messages
 
    tools = [
        {"type": "function", "function": schema_get_files_info},
        {"type": "function", "function": schema_write_file},
        {"type": "function", "function": schema_run_python_file},
        {"type": "function", "function": schema_get_file_content},
        {"type": "function", "function": schema_create_directory},
        {"type": "function", "function": schema_remove_directory},
        {"type": "function", "function": schema_remove_file},
        {"type": "function", "function": schema_move_file},
    ]
 
    response_stream = litellm.completion(
        model="gemini/gemini-2.5-flash",
        messages=full_messages,
        temperature=0,
        tools=tools,
        tool_choice="auto",
        stream=True,
    )
 
    full_content = ""
    tool_calls_acc = {}  # index -> {id, type, function: {name, arguments}}
 
    for chunk in response_stream:
        delta = chunk.choices[0].delta
 
        # ── Text chunk ────────────────────────────────────────────────────────
        if delta.content:
            full_content += delta.content
 
            # Terminal: print live
            print(delta.content, end="", flush=True)
 
            # TUI callback (called from the thread, routes into call_from_thread)
            if on_chunk:
                on_chunk(delta.content)
 
            yield {"type": "chunk", "content": delta.content}
 
        # ── Tool call delta ───────────────────────────────────────────────────
        if delta.tool_calls:
            for tc_delta in delta.tool_calls:
                idx = tc_delta.index
 
                if idx not in tool_calls_acc:
                    tool_calls_acc[idx] = {
                        "id": tc_delta.id or "",
                        "type": "function",
                        "function": {"name": "", "arguments": ""},
                    }
 
                entry = tool_calls_acc[idx]
 
                if tc_delta.id:
                    entry["id"] = tc_delta.id
                if tc_delta.function and tc_delta.function.name:
                    entry["function"]["name"] += tc_delta.function.name
                if tc_delta.function and tc_delta.function.arguments:
                    entry["function"]["arguments"] += tc_delta.function.arguments
 
    # Newline after streamed terminal output
    if full_content:
        print()
 
    tool_calls = (
        [tool_calls_acc[i] for i in sorted(tool_calls_acc)]
        if tool_calls_acc
        else None
    )
 
    # ── Final assembled message ───────────────────────────────────────────────
    yield {
        "type": "message",
        "role": "assistant",
        "content": full_content or None,
        "tool_calls": tool_calls,
    }