"""
server.py  —  root of LLM_Agent/

FastAPI scaffold. Sits in front of the existing agent backend and exposes:
  POST /chat        — accepts a user message, streams the response via SSE
  POST /clear       — clears conversation memory
  GET  /history     — returns current session history
  GET  /            — serves the frontend HTML

Run with:
  uvicorn server:app --reload --port 8000
"""

import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from agent.generate_content import generate_content
from agent.call_function import call_function
from utils.conversation_memory import load_memory, save_memory

load_dotenv()

app = FastAPI(title="Chudnelius")

# Serve static assets (CSS, JS) from /static if the folder exists
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# ── In-memory session (replaced by proper session management later) ─────────

messages: list[dict] = load_memory()


# ── SSE helper ───────────────────────────────────────────────────────────────

def sse(event: str, data: str) -> str:
    """Format a single Server-Sent Event."""
    return f"event: {event}\ndata: {data}\n\n"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the frontend."""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r") as f:
        return HTMLResponse(f.read())


@app.get("/history")
async def history():
    """Return current conversation history."""
    return JSONResponse([
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m.get("content") and m.get("role") in ("user", "assistant")
    ])


@app.post("/clear")
async def clear():
    """Wipe conversation memory."""
    messages.clear()
    save_memory(messages)
    return JSONResponse({"status": "cleared"})


@app.post("/chat")
async def chat(request: Request):
    """
    Accept a user message and stream the agent response via SSE.
    
    Expects JSON body: {"message": "user text"}
    
    SSE events emitted:
      chunk   — a streamed text fragment
      done    — agent finished, no more chunks
      tool    — a tool call is being executed (name of function)
      error   — something went wrong
    """
    body = await request.json()
    user_text = body.get("message", "").strip()
    if not user_text:
        return JSONResponse({"error": "empty message"}, status_code=400)

    messages.append({"role": "user", "content": user_text})

    async def event_stream():
        MAX_ITERATIONS = 20

        for _ in range(MAX_ITERATIONS):
            assistant_message = None
            full_content = ""

            # on_chunk fires for every streamed text fragment
            def on_chunk(text: str) -> None:
                nonlocal full_content
                full_content += text
                # Note: we yield from a sync callback, so we store chunks
                # and flush them below via the collected buffer approach.
                # For true per-chunk SSE we use the generator directly.

            # Run the blocking generator — collect events
            events = []
            for event in generate_content(messages, verbose=False, on_chunk=None):
                events.append(event)

            for event in events:
                if event["type"] == "chunk":
                    yield sse("chunk", json.dumps({"text": event["content"]}))

                elif event["type"] == "message":
                    assistant_message = event

            if assistant_message is None:
                yield sse("error", json.dumps({"text": "Empty response from agent"}))
                return

            # Append to history
            messages.append({
                k: v for k, v in assistant_message.items()
                if k != "type" and v is not None
            })

            # Tool calls — execute and loop
            if assistant_message.get("tool_calls"):
                for tool_call in assistant_message["tool_calls"]:
                    fn_name = tool_call["function"]["name"]
                    yield sse("tool", json.dumps({"text": fn_name}))
                    try:
                        fn_args = json.loads(tool_call["function"]["arguments"])
                    except (json.JSONDecodeError, TypeError):
                        fn_args = {}
                    tool_id = tool_call.get("id") or f"call_{hash(fn_name)}"
                    output = call_function(fn_name, fn_args, verbose=False)
                    messages.append({
                        "tool_call_id": tool_id,
                        "role": "tool",
                        "name": fn_name,
                        "content": str(output),
                    })
                continue

            # Text response — we're done
            save_memory(messages)
            yield sse("done", json.dumps({"text": ""}))
            return

        yield sse("error", json.dumps({"text": "Maximum iterations reached"}))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # prevents nginx buffering SSE
        }
    )
