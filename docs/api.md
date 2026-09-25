# API Reference

## Base URLs

| Environment | REST | WebSocket |
|-------------|------|-----------|
| Local | `http://localhost:8000/api/v1` | `ws://localhost:8000/api/v1/ws/learn` |
| Production | `https://learn-loop-api.onrender.com/api/v1` | `wss://learn-loop-api.onrender.com/api/v1/ws/learn` |

---

## Authentication

All endpoints (except auth) require `Authorization: Bearer <access_token>`.

### Google OAuth (PKCE)

**1. Initiate Login**
```
GET /api/v1/auth/login/google
```
→ Redirects to Supabase Google OAuth

**2. Callback**
```
GET /api/v1/auth/callback?code=<auth_code>
```
→ Sets `pkce_code_verifier` cookie, redirects to frontend `/auth/callback#access_token=...&user_id=...&email=...`

**Frontend** (`AuthCallbackPage`) extracts token from hash, stores in `localStorage`, redirects to `/`.

---

## WebSocket — Primary Interface

```
WS /api/v1/ws/learn
```

### Connect

```javascript
const ws = new WebSocket('wss://learn-loop-api.onrender.com/api/v1/ws/learn');
```

### Send Message

```json
{
  "token": "eyJ...",
  "conversation_id": "uuid-or-null",
  "message": "explain bubble sort"
}
```

### Send Action (Quick Actions)

```json
{
  "type": "action",
  "action": "continue_research|quiz_context|explain_related",
  "token": "eyJ...",
  "conversation_id": "uuid"
}
```

### Receive Events

**Phase Update** (streamed per node):
```json
{
  "type": "phase",
  "phase": "explain",
  "label": "Writing explanation"
}
```

**Final Result**:
```json
{
  "type": "result",
  "conversation_id": "uuid",
  "intent": "explain",
  "topic": "Bubble sort",
  "response": "Bubble sort is...",
  "image_path": "https://xxx.supabase.co/storage/v1/object/public/images/uuid_bubble_sort.png",
  "quiz_id": null,
  "questions": null
}
```

**Quiz Result** (includes questions):
```json
{
  "type": "result",
  "quiz_id": "uuid",
  "questions": [{"question": "..."}, ...]
}
```

**Errors**:
```json
{ "type": "auth_error", "detail": "Missing token in payload" }
{ "type": "error", "detail": "Something went wrong..." }
```

### Phase Labels

| Phase | Label |
|-------|-------|
| `classify` | Understanding your request |
| `check_sources` | Checking existing knowledge |
| `research_agent` | Researching sources |
| `auto_research` | Researching sources |
| `ingest` | Saving new sources |
| `format_research` | Preparing results |
| `explain` | Writing explanation |
| `assess` | Preparing quiz |

---

## REST Endpoints

### Conversations

**List User Conversations**
```
GET /api/v1/conversations
Authorization: Bearer <token>
```
Response:
```json
[
  { "id": "uuid", "title": "Bubble sort", "updated_at": "2026-..." }
]
```

**Get Conversation Messages**
```
GET /api/v1/conversations/{conversation_id}/messages
Authorization: Bearer <token>
```
Response:
```json
{
  "messages": [
    { "role": "user", "content": "explain bubble sort", "metadata": {}, "created_at": "..." },
    { "role": "assistant", "content": "Bubble sort...", "metadata": {"intent": "explain", "topic": "Bubble sort", "image_path": "https://..."}, "created_at": "..." }
  ]
}
```

### Assessment (Quiz)

**Get Quiz**
```
GET /api/v1/assess/{quiz_id}
Authorization: Bearer <token>
```
Response (not submitted):
```json
{ "submitted": false, "questions": [{ "question": "..." }] }
```
Response (submitted):
```json
{ "submitted": true, "correct": 2, "total": 3, "results": [...] }
```

**Submit Quiz**
```
POST /api/v1/assess/{quiz_id}/submit
Authorization: Bearer <token>
Content-Type: application/json

{ "answers": ["answer 1", "answer 2", "answer 3"] }
```
Response:
```json
{ "correct": 2, "total": 3, "results": [...] }
```

### Learn (Non-Streaming Fallback)

**Send Message**
```
POST /api/v1/learn/message
Authorization: Bearer <token>
Content-Type: application/json

{ "message": "explain bubble sort" }
```
Response: Same as WebSocket `result` type.

**Record Reaction**
```
POST /api/v1/learn/reaction
Authorization: Bearer <token>
Content-Type: application/json

{ "topic": "Bubble sort", "reaction": "too basic" }
```
Response: `{ "status": "recorded" }`

### Legacy Image Endpoint

```
GET /api/v1/learn/image/{filename}
```
**Deprecated** — Returns `410 Gone`. Use `image_path` from message response directly (Supabase public URL).

---

## Health Check

```
GET /health
```
Response: `{ "status": "ok" }`

---

## Error Responses

| Code | Meaning |
|------|---------|
| `401` | Missing/invalid/expired token |
| `403` | Resource belongs to different user |
| `404` | Not found |
| `409` | Quiz already submitted |
| `410` | Gone (legacy image endpoint) |
| `500` | Internal server error |

All errors:
```json
{ "detail": "Error description", "request_id": "uuid" }
```