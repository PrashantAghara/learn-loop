# Tech Stack

## Backend

| Component | Technology | Notes |
|-----------|------------|-------|
| **Framework** | FastAPI | Fully async, OpenAPI auto-docs |
| **Agent Orchestration** | LangGraph | State machine + streaming |
| **LLM** | `langchain-groq` → Groq `openai/gpt-oss-120b` | All reasoning, tool-calling |
| **Database Pool** | `asyncpg` | Native async Postgres driver |
| **Connection Pooling** | pgbouncer (transaction mode) | Supabase default; `statement_cache_size=0` |
| **Vector Search** | `pgvector` + HNSW index | Cosine similarity, per-user |
| **Personalization** | `mem0ai` (hosted) | Separate from RAG store |
| **JWT Verification** | `python-jose` | Local JWKS/RS256/ES256, cached |
| **HTTP Client** | `httpx` | All outbound calls |
| **Embeddings** | HuggingFace Inference API | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) |
| **Image Generation** | Pollinations.ai | Free, keyless, concept diagrams |

## Frontend

| Component | Technology | Notes |
|-----------|------------|-------|
| **Framework** | React 19 + Vite | |
| **Styling** | Tailwind CSS v4 | |
| **Routing** | `react-router-dom` | |
| **HTTP** | `axios` | Interceptors for auth + retry |
| **Markdown** | `react-markdown` + `remark-gfm` | Agent response rendering |
| **WebSocket** | Native browser `WebSocket` | Reconnect + exponential backoff |
| **Auth** | Supabase Auth (Google OAuth PKCE) | Redirect flow via `/auth/callback` |

## Data & Auth

| Service | Purpose |
|---------|---------|
| **Supabase Postgres** | Primary DB (conversations, quizzes, RAG) |
| **pgvector** | Vector similarity search |
| **Supabase Auth** | Google OAuth via PKCE |
| **Supabase Storage** | Generated images (1GB free) |
| **mem0 Cloud** | Personalization memory (independent) |

## External APIs

| API | Purpose | Auth |
|-----|---------|------|
| **Groq** | LLM (`gpt-oss-120b`) | API Key |
| **HuggingFace** | Embeddings (384-dim) | HF Token |
| **Tavily** | Live web search | API Key |
| **OpenAlex** | Academic papers | API Key |
| **Semantic Scholar** | Academic papers | API Key |
| **arXiv** | Preprints | Public |
| **Wikipedia** | Background context | Public |
| **Pollinations.ai** | Image generation | None (free) |

## Deployment

| Component | Platform | Config |
|-----------|----------|--------|
| **Backend** | Render (Docker) | `Dockerfile` |
| **Frontend** | Vercel | `vercel.json` |
| **CI/CD** | GitHub Actions | Lint + build + Docker verify on PR; deploy hooks on `main` |

## Environment Variables

### Backend (`.env`)

```bash
GROQ_API_KEY=...
OPENALEX_API_KEY=...
SUPABASE_DB_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
MEM0_API_KEY=m0-...
TAVILY_API_KEY=tvly-...
HF_TOKEN=hf_...
SEMANTIC_SCHOLAR_API_KEY=s2k-...
FRONTEND_URL=https://learn-loop-brown.vercel.app
BACKEND_URL=https://learn-loop-api.onrender.com
LOG_LEVEL=INFO
```

### Frontend (`frontend/.env`)

```bash
VITE_API_BASE=https://learn-loop-api.onrender.com/api/v1
VITE_WS_URL=wss://learn-loop-api.onrender.com/api/v1/ws/learn
```

## Why These Choices?

- **Groq + gpt-oss-120b** — Best open-weight model access with tool-calling, free tier available
- **HuggingFace Inference API for embeddings** — Moved off local `sentence-transformers`/PyTorch to fit Render free-tier memory (512MB)
- **mem0 Cloud** — Offloads personalization storage/retrieval; no local vector DB for user memory
- **Supabase pgvector** — Managed Postgres + vector extension; free tier generous
- **Pollinations.ai** — Free, keyless image generation; no API key management
- **LangGraph** — Explicit state machine beats ad-hoc orchestration for debugging