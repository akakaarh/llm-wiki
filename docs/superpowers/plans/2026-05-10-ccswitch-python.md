# ccswitch-python Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local proxy that translates OpenAI Responses API to Chat Completions API, enabling Codex CLI to work with any OpenAI-compatible backend.

**Architecture:** Three-module design — `translate.py` (pure request translation), `sse.py` (SSE stream translation), `server.py` (aiohttp HTTP layer + httpx client). All backend-agnostic, configured via environment variables.

**Tech Stack:** Python 3.11+, aiohttp, httpx, python-dotenv, pytest, uv

**Design Spec:** `docs/superpowers/specs/2026-05-10-ccswitch-python-design.md`

**Project Root:** `E:/projects/ccswitch-python/`

---

## File Structure

| File | Responsibility |
|---|---|
| `pyproject.toml` | Project metadata, dependencies, entry point |
| `.env.example` | Configuration template |
| `src/ccswitch/__init__.py` | Package marker |
| `src/ccswitch/__main__.py` | CLI entry point (uvicorn startup) |
| `src/ccswitch/config.py` | Environment variable loading via dataclass |
| `src/ccswitch/translate.py` | `translate_request()`, `translate_tools()`, `translate_content()` |
| `src/ccswitch/sse.py` | `SseTranslator` class — Chat Completions SSE → Responses API SSE |
| `src/ccswitch/server.py` | aiohttp routes, httpx streaming proxy, error handling |
| `tests/test_translate.py` | Unit tests for translate.py |
| `tests/test_sse.py` | Unit tests for sse.py |
| `README.md` | Usage documentation |

---

### Task 1: Project Setup

**Files:**
- Create: `E:/projects/ccswitch-python/pyproject.toml`
- Create: `E:/projects/ccswitch-python/.env.example`
- Create: `E:/projects/ccswitch-python/src/ccswitch/__init__.py`
- Create: `E:/projects/ccswitch-python/src/ccswitch/__main__.py`
- Create: `E:/projects/ccswitch-python/src/ccswitch/config.py`
- Create: `E:/projects/ccswitch-python/tests/__init__.py`

- [ ] **Step 1: Create project directory structure**

```bash
mkdir -p E:/projects/ccswitch-python/src/ccswitch
mkdir -p E:/projects/ccswitch-python/tests
cd E:/projects/ccswitch-python
git init
```

- [ ] **Step 2: Create pyproject.toml**

```toml
# E:/projects/ccswitch-python/pyproject.toml
[project]
name = "ccswitch"
version = "0.1.0"
description = "Responses API to Chat Completions proxy for Codex CLI"
requires-python = ">=3.11"
dependencies = [
    "aiohttp>=3.9",
    "httpx>=0.27",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]

[project.scripts]
ccswitch = "ccswitch.__main__:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/ccswitch"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 3: Create .env.example**

```bash
# E:/projects/ccswitch-python/.env.example
API_KEY=your-api-key-here
API_BASE_URL=https://api.openai.com
PROXY_HOST=127.0.0.1
PROXY_PORT=11435
DEFAULT_MODEL=gpt-4o-mini
```

- [ ] **Step 4: Create package files**

```python
# E:/projects/ccswitch-python/src/ccswitch/__init__.py
__version__ = "0.1.0"
```

```python
# E:/projects/ccswitch-python/src/ccswitch/__main__.py
import uvicorn
from ccswitch.config import load_config

def main():
    config = load_config()
    uvicorn.run(
        "ccswitch.server:app",
        host=config.proxy_host,
        port=config.proxy_port,
        log_level="info",
    )

if __name__ == "__main__":
    main()
```

```python
# E:/projects/ccswitch-python/src/ccswitch/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class Config:
    api_key: str
    api_base_url: str
    proxy_host: str
    proxy_port: int
    default_model: str

def load_config() -> Config:
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY environment variable is required")
    return Config(
        api_key=api_key,
        api_base_url=os.getenv("API_BASE_URL", "https://api.openai.com"),
        proxy_host=os.getenv("PROXY_HOST", "127.0.0.1"),
        proxy_port=int(os.getenv("PROXY_PORT", "11435")),
        default_model=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
    )
```

```python
# E:/projects/ccswitch-python/tests/__init__.py
```

- [ ] **Step 5: Install dependencies and verify**

```bash
cd E:/projects/ccswitch-python
uv sync
uv run python -c "from ccswitch.config import Config; print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "chore: initialize project structure"
```

---

### Task 2: translate.py — Message Translation

**Files:**
- Create: `E:/projects/ccswitch-python/tests/test_translate.py`
- Create: `E:/projects/ccswitch-python/src/ccswitch/translate.py`

- [ ] **Step 1: Write failing tests for content translation**

```python
# E:/projects/ccswitch-python/tests/test_translate.py
from ccswitch.translate import translate_content

def test_translate_content_input_text():
    parts = [{"type": "input_text", "text": "hello"}]
    result = translate_content(parts)
    assert result == [{"type": "text", "text": "hello"}]

def test_translate_content_output_text():
    parts = [{"type": "output_text", "text": "world"}]
    result = translate_content(parts)
    assert result == [{"type": "text", "text": "world"}]

def test_translate_content_string():
    result = translate_content("hello")
    assert result == "hello"

def test_translate_content_passthrough():
    parts = [{"type": "input_image", "image_url": "http://example.com/img.png"}]
    result = translate_content(parts)
    assert result == [{"type": "input_image", "image_url": "http://example.com/img.png"}]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'ccswitch.translate'`

- [ ] **Step 3: Implement translate_content**

```python
# E:/projects/ccswitch-python/src/ccswitch/translate.py
import logging
from typing import Any

logger = logging.getLogger(__name__)

CONTENT_TYPE_MAP = {
    "input_text": "text",
    "output_text": "text",
}


def translate_content(content: Any) -> Any:
    """Translate Responses API content to Chat Completions format."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return content
    result = []
    for part in content:
        if not isinstance(part, dict):
            result.append(part)
            continue
        new_part = dict(part)
        old_type = part.get("type")
        if old_type in CONTENT_TYPE_MAP:
            new_part["type"] = CONTENT_TYPE_MAP[old_type]
        result.append(new_part)
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py -v
```

Expected: 4 passed

- [ ] **Step 5: Write failing tests for message translation**

Append to `tests/test_translate.py`:

```python
from ccswitch.translate import translate_messages

def test_translate_user_message():
    items = [{"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hi"}]}]
    result = translate_messages(items)
    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result[0]["content"] == [{"type": "text", "text": "hi"}]

def test_translate_developer_to_system():
    items = [{"type": "message", "role": "developer", "content": [{"type": "input_text", "text": "be good"}]}]
    result = translate_messages(items)
    assert result[0]["role"] == "system"

def test_translate_assistant_message():
    items = [{"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "ok"}]}]
    result = translate_messages(items)
    assert result[0]["role"] == "assistant"
    assert result[0]["content"] == [{"type": "text", "text": "ok"}]

def test_translate_string_content():
    items = [{"type": "message", "role": "user", "content": "hello"}]
    result = translate_messages(items)
    assert result[0]["content"] == "hello"

def test_translate_no_role_defaults_to_user():
    items = [{"type": "message", "content": [{"type": "input_text", "text": "hi"}]}]
    result = translate_messages(items)
    assert result[0]["role"] == "user"
```

- [ ] **Step 6: Run tests to verify they fail**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py::test_translate_user_message -v
```

Expected: FAIL — `ImportError: cannot import name 'translate_messages'`

- [ ] **Step 7: Implement translate_messages**

Append to `src/ccswitch/translate.py`:

```python
def translate_messages(items: list[dict]) -> list[dict]:
    """Translate Responses API input items to Chat Completions messages."""
    messages = []
    for item in items:
        item_type = item.get("type")

        if item_type == "message":
            role = item.get("role", "user")
            if role == "developer":
                role = "system"
            messages.append({
                "role": role,
                "content": translate_content(item.get("content")),
            })

        elif item_type in ("function_call", "local_shell_call"):
            _append_function_call(messages, item)

        elif item_type in ("function_call_output", "local_shell_call_output", "custom_tool_call_output"):
            call_id = item.get("call_id") or item.get("id", "")
            output = item.get("output", "")
            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": translate_content(output) if isinstance(output, list) else output,
            })

        else:
            logger.warning("Unknown input item type: %s, skipping", item_type)

    return messages


def _append_function_call(messages: list[dict], item: dict) -> None:
    """Append a function_call item to the last assistant message's tool_calls."""
    call_id = item.get("call_id", "")
    name = item.get("name", "")
    arguments = item.get("arguments", "{}")

    tool_call = {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": arguments},
    }

    # Find or create assistant message
    if messages and messages[-1].get("role") == "assistant":
        msg = messages[-1]
        if msg.get("tool_calls") is None:
            msg["tool_calls"] = []
        msg["tool_calls"].append(tool_call)
    else:
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [tool_call],
        })
```

- [ ] **Step 8: Run tests to verify they pass**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py -v
```

Expected: 9 passed

- [ ] **Step 9: Write failing tests for function_call and tool output translation**

Append to `tests/test_translate.py`:

```python
def test_translate_function_call_appends_to_assistant():
    items = [
        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "let me check"}]},
        {"type": "function_call", "call_id": "call_1", "name": "get_weather", "arguments": '{"city":"Beijing"}'},
    ]
    result = translate_messages(items)
    assert len(result) == 1
    assert result[0]["role"] == "assistant"
    assert len(result[0]["tool_calls"]) == 1
    assert result[0]["tool_calls"][0]["id"] == "call_1"
    assert result[0]["tool_calls"][0]["function"]["name"] == "get_weather"

def test_translate_function_call_creates_assistant_if_needed():
    items = [
        {"type": "function_call", "call_id": "call_1", "name": "search", "arguments": '{"q":"test"}'},
    ]
    result = translate_messages(items)
    assert len(result) == 1
    assert result[0]["role"] == "assistant"
    assert result[0]["content"] is None
    assert result[0]["tool_calls"][0]["id"] == "call_1"

def test_translate_function_call_output():
    items = [
        {"type": "function_call_output", "call_id": "call_1", "output": "sunny"},
    ]
    result = translate_messages(items)
    assert result[0]["role"] == "tool"
    assert result[0]["tool_call_id"] == "call_1"
    assert result[0]["content"] == "sunny"

def test_translate_local_shell_call_output():
    items = [
        {"type": "local_shell_call_output", "id": "shell_1", "output": "file.txt"},
    ]
    result = translate_messages(items)
    assert result[0]["role"] == "tool"
    assert result[0]["tool_call_id"] == "shell_1"

def test_translate_multiple_function_calls():
    items = [
        {"type": "function_call", "call_id": "call_1", "name": "a", "arguments": "{}"},
        {"type": "function_call", "call_id": "call_2", "name": "b", "arguments": "{}"},
    ]
    result = translate_messages(items)
    assert len(result) == 1
    assert len(result[0]["tool_calls"]) == 2
```

- [ ] **Step 10: Run tests to verify they pass**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py -v
```

Expected: 14 passed (these should pass since the implementation already handles them)

- [ ] **Step 11: Commit**

```bash
git add tests/test_translate.py src/ccswitch/translate.py
git commit -m "feat: add message translation (translate_messages, translate_content)"
```

---

### Task 3: translate.py — Tools + Request Translation

**Files:**
- Modify: `E:/projects/ccswitch-python/tests/test_translate.py`
- Modify: `E:/projects/ccswitch-python/src/ccswitch/translate.py`

- [ ] **Step 1: Write failing tests for tool translation**

Append to `tests/test_translate.py`:

```python
from ccswitch.translate import translate_tools

def test_translate_tools_flat_to_nested():
    tools = [{"type": "function", "name": "get_weather", "description": "Get weather", "parameters": {"type": "object"}}]
    result = translate_tools(tools)
    assert len(result) == 1
    assert result[0]["type"] == "function"
    assert result[0]["function"]["name"] == "get_weather"
    assert result[0]["function"]["description"] == "Get weather"
    assert result[0]["function"]["parameters"] == {"type": "object"}

def test_translate_tools_filters_non_function():
    tools = [
        {"type": "function", "name": "foo", "description": "d", "parameters": {}},
        {"type": "local_shell"},
        {"type": "file_search", "vector_store_ids": ["vs1"]},
    ]
    result = translate_tools(tools)
    assert len(result) == 1
    assert result[0]["function"]["name"] == "foo"

def test_translate_tools_empty():
    assert translate_tools([]) == []
    assert translate_tools(None) is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py::test_translate_tools_flat_to_nested -v
```

Expected: FAIL — `ImportError: cannot import name 'translate_tools'`

- [ ] **Step 3: Implement translate_tools**

Append to `src/ccswitch/translate.py`:

```python
def translate_tools(tools: list[dict] | None) -> list[dict] | None:
    """Convert Responses API flat tool defs to Chat Completions nested format."""
    if not tools:
        return tools
    result = []
    for tool in tools:
        if tool.get("type") != "function":
            continue
        result.append({
            "type": "function",
            "function": {
                "name": tool.get("name", ""),
                "description": tool.get("description", ""),
                "parameters": tool.get("parameters", {}),
            },
        })
    return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py -v
```

Expected: 17 passed

- [ ] **Step 5: Write failing tests for translate_request**

Append to `tests/test_translate.py`:

```python
from ccswitch.translate import translate_request
from ccswitch.config import Config

def make_config(**kwargs):
    defaults = {"api_key": "test", "api_base_url": "http://localhost", "proxy_host": "127.0.0.1", "proxy_port": 11435, "default_model": "gpt-4o-mini"}
    defaults.update(kwargs)
    return Config(**defaults)

def test_translate_request_basic():
    body = {
        "model": "gpt-4o",
        "input": [{"type": "message", "role": "user", "content": [{"type": "input_text", "text": "hello"}]}],
        "stream": True,
    }
    result = translate_request(body, make_config())
    assert result["model"] == "gpt-4o"
    assert result["stream"] is True
    assert result["messages"][0]["role"] == "user"
    assert result["messages"][0]["content"] == [{"type": "text", "text": "hello"}]

def test_translate_request_instructions():
    body = {
        "instructions": "You are helpful",
        "input": [{"type": "message", "role": "user", "content": "hi"}],
    }
    result = translate_request(body, make_config())
    assert result["messages"][0]["role"] == "system"
    assert result["messages"][0]["content"] == "You are helpful"
    assert result["messages"][1]["role"] == "user"

def test_translate_request_string_input():
    body = {"input": "hello"}
    result = translate_request(body, make_config())
    assert len(result["messages"]) == 1
    assert result["messages"][0]["role"] == "user"
    assert result["messages"][0]["content"] == "hello"

def test_translate_request_default_model():
    body = {"input": "hello"}
    result = translate_request(body, make_config(default_model="my-model"))
    assert result["model"] == "my-model"

def test_translate_request_max_output_tokens_renamed():
    body = {"input": "hi", "max_output_tokens": 100}
    result = translate_request(body, make_config())
    assert result["max_tokens"] == 100
    assert "max_output_tokens" not in result

def test_translate_request_stream_forced():
    body = {"input": "hi", "stream": False}
    result = translate_request(body, make_config())
    assert result["stream"] is True
```

- [ ] **Step 6: Run tests to verify they fail**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py::test_translate_request_basic -v
```

Expected: FAIL — `ImportError: cannot import name 'translate_request'`

- [ ] **Step 7: Implement translate_request**

Append to `src/ccswitch/translate.py`:

```python
def translate_request(body: dict, config: Any) -> dict:
    """Convert a full Responses API request to Chat Completions format."""
    messages = []

    # Instructions → system message
    instructions = body.get("instructions")
    if instructions:
        messages.append({"role": "system", "content": instructions})

    # Input → messages
    raw_input = body.get("input", [])
    if isinstance(raw_input, str):
        raw_input = [{"type": "message", "role": "user", "content": raw_input}]
    messages.extend(translate_messages(raw_input))

    # Build Chat Completions request
    result = {
        "model": body.get("model", config.default_model),
        "messages": messages,
        "stream": True,
    }

    # Tools
    tools = translate_tools(body.get("tools"))
    if tools:
        result["tools"] = tools

    # Pass-through fields
    for field in ("temperature", "top_p", "tool_choice"):
        if field in body:
            result[field] = body[field]

    # Renamed fields
    if "max_output_tokens" in body:
        result["max_tokens"] = body["max_output_tokens"]

    return result
```

- [ ] **Step 8: Run all tests**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_translate.py -v
```

Expected: 23 passed

- [ ] **Step 9: Commit**

```bash
git add tests/test_translate.py src/ccswitch/translate.py
git commit -m "feat: add tools translation and translate_request"
```

---

### Task 4: sse.py — SSE Stream Translation

**Files:**
- Create: `E:/projects/ccswitch-python/tests/test_sse.py`
- Create: `E:/projects/ccswitch-python/src/ccswitch/sse.py`

- [ ] **Step 1: Write failing tests for basic text streaming**

```python
# E:/projects/ccswitch-python/tests/test_sse.py
import json
import pytest
from ccswitch.sse import SseTranslator


def parse_sse_events(raw: str) -> list[tuple[str, dict]]:
    """Parse raw SSE text into list of (event_type, data_dict)."""
    events = []
    current_event = None
    for line in raw.split("\n"):
        if line.startswith("event: "):
            current_event = line[len("event: "):]
        elif line.startswith("data: "):
            data = json.loads(line[len("data: "):])
            events.append((current_event, data))
    return events


@pytest.mark.asyncio
async def test_text_streaming():
    translator = SseTranslator(response_id="resp_1", model="gpt-4o")

    lines = [
        'data: {"choices":[{"delta":{"content":"Hello"}}]}',
        'data: {"choices":[{"delta":{"content":" world"}}]}',
        'data: {"choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":2,"total_tokens":12}}',
        "data: [DONE]",
    ]

    all_events = []
    for line in lines:
        events = await translator.feed(line)
        all_events.extend(events)

    done_events = await translator.done()
    all_events.extend(done_events)

    raw = "".join(all_events)
    parsed = parse_sse_events(raw)

    event_types = [e[0] for e in parsed]
    assert "response.created" in event_types
    assert "response.in_progress" in event_types
    assert "response.output_item.added" in event_types
    assert "response.content_part.added" in event_types
    assert "response.output_text.delta" in event_types
    assert "response.output_text.done" in event_types
    assert "response.content_part.done" in event_types
    assert "response.output_item.done" in event_types
    assert "response.completed" in event_types

    # Check delta content
    deltas = [e[1]["delta"] for e in parsed if e[0] == "response.output_text.delta"]
    assert deltas == ["Hello", " world"]

    # Check full text in done event
    text_done = [e for e in parsed if e[0] == "response.output_text.done"][0]
    assert text_done[1]["text"] == "Hello world"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_sse.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'ccswitch.sse'`

- [ ] **Step 3: Implement SseTranslator (text streaming)**

```python
# E:/projects/ccswitch-python/src/ccswitch/sse.py
import json
import logging
import uuid

logger = logging.getLogger(__name__)


def _sse(event_type: str, data: dict) -> str:
    """Format a single SSE event."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


class SseTranslator:
    """Translates Chat Completions SSE to Responses API SSE."""

    def __init__(self, response_id: str | None = None, model: str = "unknown"):
        self.response_id = response_id or f"resp_{uuid.uuid4().hex[:12]}"
        self.model = model
        self._started = False
        self._state = "IDLE"  # IDLE | TEXT | TOOL_CALL | DONE
        self._output_index = 0
        self._output_items = []
        self._current_text = ""
        self._current_tool_calls: dict[int, dict] = {}  # index -> {id, name, arguments}
        self._usage: dict | None = None
        self._item_id_counter = 0

    def _next_item_id(self, prefix: str = "msg") -> str:
        self._item_id_counter += 1
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def _ensure_started(self) -> list[str]:
        """Emit response.created and response.in_progress on first content."""
        if self._started:
            return []
        self._started = True
        resp = self._make_response("in_progress")
        return [
            _sse("response.created", {"type": "response.created", "response": resp}),
            _sse("response.in_progress", {"type": "response.in_progress", "response": resp}),
        ]

    def _make_response(self, status: str) -> dict:
        return {
            "id": self.response_id,
            "object": "response",
            "status": status,
            "model": self.model,
            "output": list(self._output_items),
            "usage": self._usage or {},
        }

    async def feed(self, line: str) -> list[str]:
        """Process one SSE line from Chat Completions stream."""
        line = line.strip()
        if not line:
            return []
        if line == "data: [DONE]":
            return await self._finish_current_item()

        if not line.startswith("data: "):
            return []

        try:
            chunk = json.loads(line[6:])
        except json.JSONDecodeError:
            logger.warning("Failed to parse SSE chunk: %s", line)
            return []

        # Extract usage if present
        if "usage" in chunk:
            self._usage = chunk["usage"]

        choices = chunk.get("choices", [])
        if not choices:
            return []

        delta = choices[0].get("delta", {})
        finish_reason = choices[0].get("finish_reason")

        events = []

        # Handle text content
        if "content" in delta and delta["content"]:
            events.extend(self._handle_text_delta(delta["content"]))

        # Handle tool calls
        if "tool_calls" in delta:
            events.extend(self._handle_tool_calls_delta(delta["tool_calls"]))

        # Handle finish
        if finish_reason:
            events.extend(await self._handle_finish(finish_reason))

        return events

    def _handle_text_delta(self, text: str) -> list[str]:
        events = self._ensure_started()

        if self._state != "TEXT":
            # Flush any pending tool calls
            events.extend(self._flush_tool_calls())
            # Start new text output item
            self._state = "TEXT"
            self._current_text = ""
            item_id = self._next_item_id("msg")
            self._current_item_id = item_id
            item = {"type": "message", "id": item_id, "status": "in_progress", "role": "assistant", "content": []}
            events.append(_sse("response.output_item.added", {"type": "response.output_item.added", "output_index": self._output_index, "item": item}))
            events.append(_sse("response.content_part.added", {"type": "response.content_part.added", "item_id": item_id, "output_index": self._output_index, "content_index": 0, "part": {"type": "output_text", "text": "", "annotations": []}}))

        self._current_text += text
        events.append(_sse("response.output_text.delta", {"type": "response.output_text.delta", "item_id": self._current_item_id, "output_index": self._output_index, "content_index": 0, "delta": text}))
        return events

    def _handle_tool_calls_delta(self, tool_calls: list[dict]) -> list[str]:
        events = self._ensure_started()

        for tc in tool_calls:
            idx = tc.get("index", 0)
            if idx not in self._current_tool_calls:
                # Flush pending text if any
                events.extend(self._flush_text())
                # Start new tool call
                self._state = "TOOL_CALL"
                item_id = self._next_item_id("fc")
                self._current_tool_calls[idx] = {
                    "id": tc.get("id", ""),
                    "name": tc.get("function", {}).get("name", ""),
                    "arguments": "",
                    "item_id": item_id,
                }
                # We'll emit output_item.added when we have the name
                # (first chunk may only have id)

            call = self._current_tool_calls[idx]

            # Update id if provided
            if tc.get("id"):
                call["id"] = tc["id"]
            # Update name if provided
            if tc.get("function", {}).get("name"):
                call["name"] = tc["function"]["name"]
            # Append arguments
            args_delta = tc.get("function", {}).get("arguments", "")
            if args_delta:
                call["arguments"] += args_delta
                # Emit added event if not yet emitted
                if not call.get("added_emitted"):
                    call["added_emitted"] = True
                    item = {"type": "function_call", "id": call["item_id"], "call_id": call["id"], "name": call["name"], "arguments": "", "status": "in_progress"}
                    events.append(_sse("response.output_item.added", {"type": "response.output_item.added", "output_index": self._output_index, "item": item}))

                events.append(_sse("response.function_call_arguments.delta", {"type": "response.function_call_arguments.delta", "item_id": call["item_id"], "output_index": self._output_index, "delta": args_delta}))

        return events

    def _flush_text(self) -> list[str]:
        """Finish current text output item if any."""
        if self._state != "TEXT":
            return []
        events = []
        events.append(_sse("response.output_text.done", {"type": "response.output_text.done", "item_id": self._current_item_id, "output_index": self._output_index, "content_index": 0, "text": self._current_text}))
        events.append(_sse("response.content_part.done", {"type": "response.content_part.done", "item_id": self._current_item_id, "output_index": self._output_index, "content_index": 0, "part": {"type": "output_text", "text": self._current_text, "annotations": []}}))
        item = {"type": "message", "id": self._current_item_id, "status": "completed", "role": "assistant", "content": [{"type": "output_text", "text": self._current_text, "annotations": []}]}
        events.append(_sse("response.output_item.done", {"type": "response.output_item.done", "output_index": self._output_index, "item": item}))
        self._output_items.append(item)
        self._output_index += 1
        self._current_text = ""
        self._state = "IDLE"
        return events

    def _flush_tool_calls(self) -> list[str]:
        """Finish all pending tool call items."""
        if self._state != "TOOL_CALL":
            return []
        events = []
        for idx in sorted(self._current_tool_calls.keys()):
            call = self._current_tool_calls[idx]
            # If added wasn't emitted (no args received), emit it now
            if not call.get("added_emitted"):
                item = {"type": "function_call", "id": call["item_id"], "call_id": call["id"], "name": call["name"], "arguments": call["arguments"], "status": "in_progress"}
                events.append(_sse("response.output_item.added", {"type": "response.output_item.added", "output_index": self._output_index, "item": item}))

            events.append(_sse("response.function_call_arguments.done", {"type": "response.function_call_arguments.done", "item_id": call["item_id"], "output_index": self._output_index, "arguments": call["arguments"]}))
            item = {"type": "function_call", "id": call["item_id"], "call_id": call["id"], "name": call["name"], "arguments": call["arguments"], "status": "completed"}
            events.append(_sse("response.output_item.done", {"type": "response.output_item.done", "output_index": self._output_index, "item": item}))
            self._output_items.append(item)
            self._output_index += 1
        self._current_tool_calls.clear()
        self._state = "IDLE"
        return events

    async def _handle_finish(self, finish_reason: str) -> list[str]:
        """Handle finish_reason from backend."""
        if finish_reason == "stop":
            return self._flush_text()
        elif finish_reason == "tool_calls":
            return self._flush_tool_calls()
        return []

    async def _finish_current_item(self) -> list[str]:
        """Called when stream ends ([DONE])."""
        events = []
        events.extend(self._flush_text())
        events.extend(self._flush_tool_calls())
        return events

    async def done(self) -> list[str]:
        """Called after stream is fully consumed. Emits response.completed."""
        # Ensure any pending items are flushed
        events = []
        events.extend(self._flush_text())
        events.extend(self._flush_tool_calls())

        status = "completed"
        resp = self._make_response(status)
        events.append(_sse("response.completed", {"type": "response.completed", "response": resp}))
        self._state = "DONE"
        return events
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_sse.py -v
```

Expected: 1 passed

- [ ] **Step 5: Write failing tests for tool call streaming**

Append to `tests/test_sse.py`:

```python
@pytest.mark.asyncio
async def test_tool_call_streaming():
    translator = SseTranslator(response_id="resp_2", model="gpt-4o")

    lines = [
        'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_123","function":{"name":"get_weather","arguments":""}}]}}]}',
        'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"{\\"city\\":"}}]}}]}',
        'data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"\\"Beijing\\"}"}}]}}]}',
        'data: {"choices":[{"delta":{},"finish_reason":"tool_calls"}]}',
        "data: [DONE]",
    ]

    all_events = []
    for line in lines:
        events = await translator.feed(line)
        all_events.extend(events)
    done_events = await translator.done()
    all_events.extend(done_events)

    raw = "".join(all_events)
    parsed = parse_sse_events(raw)

    event_types = [e[0] for e in parsed]
    assert "response.output_item.added" in event_types
    assert "response.function_call_arguments.delta" in event_types
    assert "response.function_call_arguments.done" in event_types
    assert "response.output_item.done" in event_types
    assert "response.completed" in event_types

    # Check arguments accumulated correctly
    args_done = [e for e in parsed if e[0] == "response.function_call_arguments.done"][0]
    assert args_done[1]["arguments"] == '{"city":"Beijing"}'

    # Check output item
    item_done = [e for e in parsed if e[0] == "response.output_item.done"][0]
    assert item_done[1]["item"]["name"] == "get_weather"
    assert item_done[1]["item"]["call_id"] == "call_123"


@pytest.mark.asyncio
async def test_empty_stream():
    translator = SseTranslator(response_id="resp_3", model="gpt-4o")
    done_events = await translator.done()
    raw = "".join(done_events)
    parsed = parse_sse_events(raw)
    event_types = [e[0] for e in parsed]
    assert "response.completed" in event_types
    completed = [e for e in parsed if e[0] == "response.completed"][0]
    assert completed[1]["response"]["output"] == []
```

- [ ] **Step 6: Run all tests**

```bash
cd E:/projects/ccswitch-python
uv run pytest tests/test_sse.py -v
```

Expected: 3 passed

- [ ] **Step 7: Commit**

```bash
git add tests/test_sse.py src/ccswitch/sse.py
git commit -m "feat: add SSE stream translator (SseTranslator)"
```

---

### Task 5: server.py — HTTP Layer

**Files:**
- Create: `E:/projects/ccswitch-python/src/ccswitch/server.py`

- [ ] **Step 1: Implement server.py**

```python
# E:/projects/ccswitch-python/src/ccswitch/server.py
import json
import logging
import uuid

import aiohttp
from aiohttp import web

import httpx

from ccswitch.config import Config, load_config
from ccswitch.translate import translate_request
from ccswitch.sse import SseTranslator

logger = logging.getLogger(__name__)

try:
    config = load_config()
except ValueError as e:
    logger.error("Configuration error: %s", e)
    config = None


def _error_sse(code: str, message: str) -> str:
    """Format an error as Responses API SSE event."""
    data = json.dumps({"type": "error", "code": code, "message": message})
    return f"event: error\ndata: {data}\n\n"


async def handle_responses(request: web.Request) -> web.StreamResponse:
    """Main proxy endpoint: POST /v1/responses"""
    if config is None:
        return web.Response(status=500, text="Server not configured")

    # Parse request body
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    # Translate to Chat Completions format
    chat_body = translate_request(body, config)

    # Build backend URL
    backend_url = f"{config.api_base_url.rstrip('/')}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
    }

    # Create SSE response
    response = web.StreamResponse(
        status=200,
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
    await response.prepare(request)

    response_id = f"resp_{uuid.uuid4().hex[:12]}"
    model = chat_body.get("model", config.default_model)
    translator = SseTranslator(response_id=response_id, model=model)

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream(
                "POST",
                backend_url,
                json=chat_body,
                headers=headers,
            ) as resp:
                if resp.status_code != 200:
                    error_body = await resp.aread()
                    try:
                        error_data = json.loads(error_body)
                        msg = error_data.get("error", {}).get("message", error_body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        msg = str(error_body)
                    error_event = _error_sse("backend_error", f"Backend returned {resp.status_code}: {msg}")
                    await response.write(error_event.encode())
                    await response.write_eof()
                    return response

                async for line in resp.aiter_lines():
                    events = await translator.feed(line)
                    for event in events:
                        await response.write(event.encode())

        # Emit completion events
        done_events = await translator.done()
        for event in done_events:
            await response.write(event.encode())

    except httpx.ConnectError:
        error_event = _error_sse("connection_error", f"Cannot connect to backend at {config.api_base_url}")
        await response.write(error_event.encode())
    except httpx.TimeoutException:
        error_event = _error_sse("timeout", "Backend request timed out")
        await response.write(error_event.encode())
    except Exception as e:
        logger.exception("Unexpected error")
        error_event = _error_sse("internal_error", str(e))
        await response.write(error_event.encode())

    await response.write_eof()
    return response


async def handle_models(request: web.Request) -> web.Response:
    """GET /v1/models — minimal model list."""
    data = {
        "object": "list",
        "data": [
            {
                "id": config.default_model if config else "default",
                "object": "model",
                "owned_by": "ccswitch",
            }
        ],
    }
    return web.json_response(data)


async def handle_health(request: web.Request) -> web.Response:
    """GET / — health check."""
    return web.json_response({"status": "ok", "service": "ccswitch"})


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/v1/responses", handle_responses)
    app.router.add_post("/responses", handle_responses)
    app.router.add_get("/v1/models", handle_models)
    app.router.add_get("/", handle_health)
    return app


app = create_app()
```

- [ ] **Step 2: Verify the app loads**

```bash
cd E:/projects/ccswitch-python
uv run python -c "from ccswitch.server import app; print(f'Routes: {[r.path for r in app.router.routes()]}')"
```

Expected: Routes list including `/v1/responses`, `/responses`, `/v1/models`, `/`

- [ ] **Step 3: Commit**

```bash
git add src/ccswitch/server.py
git commit -m "feat: add HTTP server with streaming proxy"
```

---

### Task 6: README + Final Integration

**Files:**
- Create: `E:/projects/ccswitch-python/README.md`

- [ ] **Step 1: Write README**

```markdown
# ccswitch-python

A local proxy that translates OpenAI's Responses API to Chat Completions API, enabling Codex CLI to work with any OpenAI-compatible backend.

## How It Works

```
Codex ──Responses API──> localhost:11435 ──Chat Completions──> Any backend
```

## Quick Start

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/ccswitch-python.git
cd ccswitch-python
uv sync

# Configure
cp .env.example .env
# Edit .env with your API_KEY and API_BASE_URL

# Run
uv run python -m ccswitch
```

## Codex CLI Setup

Add to `~/.codex/config.toml`:

```toml
[model_providers.ccswitch]
base_url = "http://127.0.0.1:11435/v1"
wire_api = "responses"
```

Then run: `codex --profile ccswitch`

## Configuration

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | (required) | Backend API key |
| `API_BASE_URL` | `https://api.openai.com` | Backend base URL |
| `PROXY_HOST` | `127.0.0.1` | Listen address |
| `PROXY_PORT` | `11435` | Listen port |
| `DEFAULT_MODEL` | `gpt-4o-mini` | Default model |

## Supported Backends

Any OpenAI-compatible Chat Completions API:
- OpenAI
- DeepSeek
- mimo (via compatible endpoint)
- Ollama (with OpenAI compatibility mode)
- vLLM, LiteLLM, etc.

## Testing

```bash
uv run pytest
```
```

- [ ] **Step 2: Verify end-to-end with curl**

```bash
cd E:/projects/ccswitch-python
# Start proxy in background (need a real API key for this)
# uv run python -m ccswitch &

# Test health endpoint
# curl http://127.0.0.1:11435/

# Test models endpoint
# curl http://127.0.0.1:11435/v1/models
```

(Manual verification step — requires running proxy with valid API key)

- [ ] **Step 3: Run all tests one final time**

```bash
cd E:/projects/ccswitch-python
uv run pytest -v
```

Expected: All tests pass

- [ ] **Step 4: Final commit**

```bash
git add README.md
git commit -m "docs: add README with usage instructions"
```

---

## Summary

| Task | What it builds | Tests |
|---|---|---|
| 1 | Project skeleton + config | — |
| 2 | `translate_messages` + `translate_content` | 14 unit tests |
| 3 | `translate_tools` + `translate_request` | 9 unit tests |
| 4 | `SseTranslator` (SSE stream translation) | 3 async tests |
| 5 | `server.py` (HTTP layer) | Manual verification |
| 6 | README + integration | Final test run |

Total: ~26 unit tests covering all translation logic.
