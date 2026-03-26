# HDT Behavioral Monitoring (FastAPI)

This service stores and retrieves user interaction events.

From your screenshot ("Behavioral Monitoring Actions"), these gateway paths are implemented:

- `POST /users/actions` (store user interactions)
- `GET /users/actions` (retrieve user interactions)

Additional implemented endpoints:

- `POST /users/actions/batch` (store actions in batch)
- `GET /users/sessions` (list tracked sessions)
- `GET /users/{user_id}/summary` (aggregated user behavior summary)

These routes are exposed through `HDT-API-Gateway` via `/users/*`.

## Run

1. Install dependencies
   - `pip install -r requirements.txt`
2. Start the server
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000`

## Endpoints

### Store user interactions

`POST /users/actions`

Body (JSON, example):
```json
{
  "user_id": "u-1",
  "session_id": "s-1",
  "action_type": "click",
  "page": "/dashboard",
  "metadata": {
    "x": 100,
    "y": 220
  }
}
```

### Retrieve user interactions

`GET /users/actions?user_id=u-1&session_id=s-1&action_type=click&limit=50&offset=0`

