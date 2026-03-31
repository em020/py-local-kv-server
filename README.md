# py-local-kv-server

A minimalist local key-value (KV) HTTP server built with [FastAPI](https://fastapi.tiangolo.com/). Store and retrieve string values by key over HTTP, with optional TTL-based expiry and automatic JSON persistence across restarts.

## Features

- **Save & retrieve** string values via a simple REST API
- **TTL support** — entries expire automatically (default: 4 hours)
- **Persistence** — the store is saved to a JSON file and reloaded on startup (expired entries are skipped)
- **Atomic writes** — the store file is updated atomically to avoid corruption
- **Configurable** via environment variables

## Requirements

- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/) `>=0.100.0`
- [Uvicorn](https://www.uvicorn.org/) `>=0.23.0`

## Installation

```bash
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

The interactive API docs are available at `http://127.0.0.1:8000/docs` once the server is running.

## Configuration

| Environment variable | Default          | Description                                   |
|----------------------|------------------|-----------------------------------------------|
| `KV_STORE_FILE`      | `kv_store.json`  | Path to the JSON file used for persistence    |

## API

### `POST /save_string`

Store a string value under a key.

**Request body (JSON)**

| Field         | Type    | Required | Description                                        |
|---------------|---------|----------|----------------------------------------------------|
| `key`         | string  | Yes      | The key to store the value under                   |
| `value`       | string  | Yes      | The string value to store                          |
| `ttl_seconds` | integer | No       | Time-to-live in seconds (default: 14400 / 4 hours) |

**Example**

```bash
curl -X POST http://127.0.0.1:8000/save_string \
  -H "Content-Type: application/json" \
  -d '{"key": "greeting", "value": "hello", "ttl_seconds": 3600}'
```

**Response**

```json
{"status": "ok"}
```

---

### `GET /retrieve_string`

Retrieve the string value stored under a key.

**Query parameter**

| Parameter | Type   | Required | Description              |
|-----------|--------|----------|--------------------------|
| `key`     | string | Yes      | The key to look up       |

**Example**

```bash
curl "http://127.0.0.1:8000/retrieve_string?key=greeting"
```

**Response**

```json
{"key": "greeting", "value": "hello"}
```

Returns `404` if the key does not exist or has expired.

## Running tests

```bash
pip install pytest httpx
pytest tests/
```
