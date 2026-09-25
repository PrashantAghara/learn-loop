# Local Setup

## Prerequisites

- Python 3.12+
- Node.js 18+
- `uv` (Python package manager) — `pip install uv`
- Supabase project (Postgres + Auth + Storage)
- API keys for: Groq, OpenAlex, Tavily, HuggingFace, mem0, Semantic Scholar

---

## 1. Supabase Setup

### Database

1. Create project at https://supabase.com
2. Enable **pgvector** extension:
   ```sql
   create extension if not exists vector;
   ```
3. Run the schema from [schema.md](schema.md) in SQL Editor
4. Create **Storage bucket** named `images` → set to **Public**

### Auth

1. Authentication → Providers → Enable **Google**
2. Add authorized redirect URI:
   ```
   https://<your-project>.supabase.co/auth/v1/callback
   ```
3. Copy **Project URL** and **Publishable Key** (anon key)

---

## 2. Backend

```bash
cd D:\resume-projects\learn-loop

# Install dependencies
uv sync

# Create .env from template
cp .env.example .env  # or create manually
```

### `.env` (Backend)

```bash
# Required
GROQ_API_KEY=gsk_...
OPENALEX_API_KEY=...
SUPABASE_DB_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
MEM0_API_KEY=m0-...
TAVILY_API_KEY=tvly-dev-...
HF_TOKEN=hf_...
SEMANTIC_SCHOLAR_API_KEY=s2k-...

# Optional (defaults shown)
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
LOG_LEVEL=INFO
```

### Run Backend

```bash
uvicorn app.main:app --reload --reload-dir app
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger UI)
```

---

## 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env
cat > .env << EOF
VITE_API_BASE=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/ws/learn
EOF
```

### Run Frontend

```bash
npm run dev
# → http://localhost:5173
```

---

## 4. Verify

1. Open http://localhost:5173
2. Click "Login with Google"
3. Complete OAuth flow → redirected to `/auth/callback` → home
4. Send a message → should get streaming response via WebSocket

---

## Docker (Optional)

```bash
# Build
docker build -t learn-loop .

# Run
docker run -p 8000:8000 --env-file .env learn-loop
```

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | `uv sync` |
| `401 JWKS fetch` | Check `SUPABASE_PUBLISHABLE_KEY` in `.env` |
| `pgbouncer prepared statement` | Already fixed: `statement_cache_size=0` in `app/core/database.py` |
| `CORS error` | Add `http://localhost:5173` to `allow_origins` in `app/main.py` |
| `WebSocket 403` | Token expired — re-login |
| `Image 404` | Create `images` bucket in Supabase Storage, set Public |
| `HF embedding 503` | Normal on cold start — retries with backoff (max 20s) in `embed_texts()` |

---

## Environment-Specific Notes

### Production (Render + Vercel)

- Backend: Set env vars in Render dashboard
- Frontend: Set `VITE_API_BASE`, `VITE_WS_URL` in Vercel dashboard
- `FRONTEND_URL` = Vercel deployment URL
- `BACKEND_URL` = Render service URL

### Free Tier Limits

- **Render**: Spins down after 15 min inactivity (cold start ~30s)
- **Supabase**: 500MB DB, 1GB Storage, 2GB bandwidth/month
- **Groq**: Rate limits on free tier
- **HuggingFace**: Inference API rate limits + cold starts on embedding model