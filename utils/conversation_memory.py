"""
utils/conversation_memory.py

Persists conversation history to a local JSON file so sessions survive
restarts. Only user and assistant messages are saved — tool call payloads
are stripped out since they're not needed for display and can be large.

Memory is capped at MAX_PAIRS exchanges (user + assistant = 1 pair) so
local models aren't burdened by an ever-growing context window.
"""

import json
import os

MEMORY_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "memory.json")

# Maximum number of user/assistant exchanges to keep in memory.
# 1 pair = 1 user message + 1 assistant reply.
# Raise this if you have a model with a large context window;
# lower it if you're running something small locally.
MAX_PAIRS = 20


def _ensure_dir() -> None:
    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)


def _trim_to_window(messages: list[dict]) -> list[dict]:
    """
    Return at most MAX_PAIRS user/assistant exchanges from the end of
    the message list. Pairs are counted from the most recent backwards
    so the freshest context is always preserved.
    """
    pairs_seen = 0
    cutoff = len(messages)

    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "assistant":
            pairs_seen += 1
        if pairs_seen >= MAX_PAIRS:
            cutoff = i
            break

    return messages[cutoff:]


def load_memory() -> list[dict]:
    """Return persisted messages, trimmed to the window, or [] if none exist."""
    _ensure_dir()
    if not os.path.exists(MEMORY_PATH):
        return []
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return _trim_to_window(data)
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_memory(messages: list[dict]) -> None:
    """
    Persist messages to disk, trimmed to MAX_PAIRS.
    Strips tool-role messages and raw tool_calls payloads to keep the
    file clean and safe to replay into the model on next load.
    """
    _ensure_dir()

    # Strip ephemeral tool traffic before trimming
    saveable = []
    for msg in messages:
        role = msg.get("role")
        if role == "tool":
            continue
        content = msg.get("content")
        if content:
            saveable.append({"role": role, "content": content})

    saveable = _trim_to_window(saveable)

    try:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(saveable, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"[memory] Could not save: {e}")


def clear_memory() -> None:
    """Delete the memory file entirely."""
    if os.path.exists(MEMORY_PATH):
        os.remove(MEMORY_PATH)