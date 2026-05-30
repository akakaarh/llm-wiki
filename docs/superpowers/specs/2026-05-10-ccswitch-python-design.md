# ccswitch-python Design Spec

**Date:** 2026-05-10
**Status:** Approved
**Reference:** https://github.com/liuzhengming/ccswitch-deepseek

## Problem

OpenAI Codex CLI uses the Responses API protocol (`POST /v1/responses`). Most third-party model providers (mimo, DeepSeek, Ollama, etc.) only offer the Chat Completions API (`POST /v1/chat/completions`). A local proxy is needed to translate between these two protocols, enabling Codex to work with any OpenAI-compatible backend.

## Goals

- Enable Codex CLI to use any Chat Completions-compatible backend
- Backend-agnostic: no backend-specific hacks or assumptions
- Clean protocol translation based on the official Responses API spec
- Configurable via environment variables
- Usable as a local tool (no auth, no database)

## Non-Goals (MVP)

- Multi-backend profile switching
- Tool filtering by domain (backend-specific optimization)
- MCP namespace handling
- DSML recovery (DeepSeek-specific bug workaround)
- `previous_response_id` stateful chaining
- Reasoning/thinking mode mapping

## Architecture

```
Codex ──Responses API──> localhost:11435 ──Chat Completions──> Any backend
```

Three modules with clear responsibilities:

| Module | Responsibility | I/O |
|---|---|---|
| `translate.py` | Protocol translation (request direction) | Pure functions, no I/O |
| `sse.py` | SSE stream translation (response direction) | Pure async generator, no HTTP |
| `server.py` | HTTP routing, streaming proxy | aiohttp server + httpx client |

## Tech Stack

- **Language:** Python 3.11+
- **Package manager:** uv
- **HTTP server:** aiohttp
- **HTTP client:** httpx (async streaming)
- **Config:** python-dotenv + dataclass
- **Testing:** pytest + pytest-asyncio

## Project Structure

```
ccswitch-python/
├── README.md
├── pyproject.toml
├── .env.example
├── src/ccswitch/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py
│   ├── translate.py
│   ├── sse.py
│   └── config.py
└── tests/
    ├── test_translate.py
    └── test_sse.py
```

## Configuration

Environment variables (loaded from `.env` or shell):

| Variable | Required | Default | Description |
|---|---|---|---|
| `API_KEY` | Yes | — | Backend API key |
| `API_BASE_URL` | No | `https://api.openai.com` | Backend base URL |
| `PROXY_HOST` | No | `127.0.0.1` | Proxy listen address |
| `PROXY_PORT` | No | `11435` | Proxy listen port |
| `DEFAULT_MODEL` | No | `gpt-4o-mini` | Default model name |

## Module Design

### translate.py — Request Translation

Core function:

```python
def translate_request(body: dict, config: Config) -> dict:
    """Convert Responses API request to Chat Completions request."""
```

**Input → Messages translation:**

1. If `instructions` present, prepend `{role: "system", content: instructions}`
2. If `input` is a string, convert to `[{type: "message", role: "user", content: input}]`
3. Iterate `input` array, dispatch by item type:

| item.type | Translation |
|---|---|
| `message` (role=user/assistant) | Map directly, rewrite content types |
| `message` (role=developer) | Change role to `system` |
| `function_call` | Append to previous assistant's `tool_calls[]`; if none exists, create `{role:"assistant", content:null, tool_calls:[...]}` |
| `local_shell_call` | Same as `function_call` (Codex replays shell calls as tool calls) |
| `function_call_output` | `{role: "tool", tool_call_id: call_id, content: output}` |
| `local_shell_call_output` | `{role: "tool", tool_call_id: id, content: output}` |
| `custom_tool_call_output` | `{role: "tool", tool_call_id: call_id, content: output}` |
| Other | Skip with warning log |

3. Content type rewriting:
   - `input_text` → `text`
   - `output_text` → `text`
   - `input_image` → pass through
   - String content → use directly

**Tools translation:**

- Filter out non-function tools (e.g., `local_shell`, `file_search`)
- Convert flat format to nested:
  - Input: `{type:"function", name:"foo", description:"...", parameters:{...}}`
  - Output: `{type:"function", function:{name:"foo", description:"...", parameters:{...}}}`

**Field mapping:**

| Responses API field | Chat Completions field | Action |
|---|---|---|
| `model` | `model` | Keep, or use `DEFAULT_MODEL` |
| `temperature` | `temperature` | Pass through |
| `top_p` | `top_p` | Pass through |
| `max_output_tokens` | `max_tokens` | Rename |
| `tool_choice` | `tool_choice` | Pass through |
| `parallel_tool_calls` | — | Ignore (not in Chat Completions spec) |
| `stream` | `stream` | Force `true` |
| `reasoning` | — | Ignore (MVP) |
| `previous_response_id` | — | Ignore (MVP) |

### sse.py — SSE Stream Translation

```python
class SseTranslator:
    def __init__(self, response_id: str, model: str): ...
    async def feed(self, line: str) -> list[str]: ...
    async def done(self) -> list[str]: ...
```

**State machine:**

```
IDLE → STARTED → (TEXT | TOOL_CALL) → DONE
```

- `IDLE`: On first delta, emit `response.created` + `response.in_progress`
- `TEXT`: Emit `output_item.added` → `content_part.added` → `output_text.delta` × N → `output_text.done` → `content_part.done` → `output_item.done`
- `TOOL_CALL`: Emit `output_item.added` → `function_call_arguments.delta` × N → `function_call_arguments.done` → `output_item.done`
- `DONE`: On `[DONE]`, emit `response.completed` with full output array and usage

**Key details:**

- Lazy start: `response.created`/`response.in_progress` emitted only on first actual content
- Multiple output items: each gets its own `added → deltas → done` sequence
- Tool call accumulation: `delta.tool_calls` may arrive in multiple chunks per index
- Usage extraction: captured from backend chunks, included in `response.completed`
- SSE format: `event: <type>\ndata: <json>\n\n` (the `event:` header is mandatory)

### server.py — HTTP Layer

**Routes:**

| Method | Path | Handler |
|---|---|---|
| `POST` | `/v1/responses` | `handle_responses` |
| `POST` | `/responses` | `handle_responses` (alias) |
| `GET` | `/v1/models` | `handle_models` |
| `GET` | `/` | `handle_health` |

**handle_responses flow:**

1. Parse request body as JSON
2. `translate_request(body, config)` → Chat Completions body
3. httpx streaming POST to `{API_BASE_URL}/v1/chat/completions`
4. If backend returns non-200: read error body, return as Responses API error event
5. Create `SseTranslator`
6. Create `StreamResponse` with `Content-Type: text/event-stream`
7. Iterate backend SSE lines → `translator.feed(line)` → write events
8. `translator.done()` → write completion events
9. Write EOF

**Error handling:**

| Scenario | Response |
|---|---|
| Backend 4xx/5xx | Forward error as `event: error\ndata: {"type":"error","code":"...","message":"..."}` |
| Backend connection timeout | 504 + error event |
| Backend connection refused | 502 + error event |
| Request body parse failure | 400 |
| Unknown exception | 500 + log |

**GET /v1/models:**

Returns a minimal model list so Codex doesn't error:
```json
{"object": "list", "data": [{"id": "default", "object": "model", "owned_by": "ccswitch"}]}
```

Optionally proxies to backend's `/v1/models` if available.

## Testing Strategy

**Phase 1 — Unit tests (no network):**

- `test_translate.py`: Construct Responses API bodies → call `translate_request()` → assert Chat Completions format
- `test_sse.py`: Feed Chat Completions SSE lines → assert Responses API event sequence

**Phase 2 — Integration test (curl):**

Script that sends simulated Responses API requests to the proxy and validates SSE output.

**Phase 3 — End-to-end (Codex CLI):**

Install Codex CLI, configure `base_url`, run actual conversations.

## Verification Steps

1. `uv sync` to install dependencies
2. Create `.env` with backend API key and URL
3. `uv run python -m ccswitch` to start proxy
4. `curl` test with simulated request
5. `uv run pytest` for unit tests
6. Install Codex CLI, configure `~/.codex/config.toml`:
   ```toml
   [model_providers.ccswitch]
   base_url = "http://127.0.0.1:11435/v1"
   wire_api = "responses"
   ```
7. `codex --profile ccswitch` to test real conversation

## Future Enhancements

- **Tool filtering:** `MAX_TOOLS` config + domain keyword priority trimming
- **Namespace handling:** MCP tool name `___` separator
- **DSML recovery:** Recover tool calls leaked as plain text XML
- **Thinking mode:** Map `reasoning` field to backend thinking parameters
- **Multi-profile:** Config file with multiple backend profiles
- **`previous_response_id`:** Stateful multi-turn support (cache historical responses)
- **WebSocket transport:** Support Codex's WebSocket mode
