# Database Schema

Everything lives in Supabase Postgres. Two categories: a per-user RAG corpus, and conversation/quiz state.

---

## RAG Corpus — `paper_chunks`

One row per chunk, scoped per user so research isn't shared across accounts.

```sql
create table paper_chunks (
    id uuid primary key default gen_random_uuid(),
    paper_title text not null,
    paper_url text,
    source text,                  -- 'arxiv' | 'openalex' | 'semantic_scholar' | 'wikipedia' | 'tavily'
    chunk_text text not null,
    embedding vector(384) not null,
    metadata jsonb default '{}'::jsonb,   -- { year, citation_count }
    user_id text not null,
    created_at timestamptz default now()
);

create index paper_chunks_user_idx on paper_chunks(user_id);
create index paper_chunks_embedding_idx on paper_chunks using hnsw (embedding vector_cosine_ops);
```

### Similarity Search Function

Cosine similarity search, scoped to one user.

```sql
create function match_paper_chunks(query_embedding vector(384), match_count int, p_user_id text)
returns table (
    id uuid,
    paper_title text,
    paper_url text,
    source text,
    chunk_text text,
    similarity float
)
language plpgsql as $$
begin
    return query
    select paper_chunks.id, paper_chunks.paper_title, paper_chunks.paper_url,
           paper_chunks.source, paper_chunks.chunk_text,
           1 - (paper_chunks.embedding <=> query_embedding) as similarity
    from paper_chunks
    where paper_chunks.user_id = p_user_id
    order by paper_chunks.embedding <=> query_embedding
    limit match_count;
end;
$$;
```

---

## Conversations — `conversations`

Sidebar history.

```sql
create table conversations (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    title text,                   -- LLM-generated, 5 words, on the first message
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create index conversations_user_idx on conversations(user_id, updated_at desc);
```

---

## Messages — `chat_messages`

```sql
create table chat_messages (
    id uuid primary key default gen_random_uuid(),
    conversation_id uuid not null references conversations(id) on delete cascade,
    role text not null,           -- 'user' | 'assistant'
    content text,
    metadata jsonb default '{}'::jsonb,   -- { intent, topic, image_path, quiz_id }
    created_at timestamptz default now()
);

create index chat_messages_conversation_idx on chat_messages(conversation_id, created_at);
```

### Metadata Structure

```json
{
  "intent": "explain",
  "topic": "Bubble sort",
  "image_path": "https://xxx.supabase.co/storage/v1/object/public/images/uuid_diagram.png",
  "quiz_id": "uuid"
}
```

---

## Quiz Sessions — `quiz_sessions`

Persisted so a reload or restart doesn't lose an in-progress quiz.

```sql
create table quiz_sessions (
    id uuid primary key default gen_random_uuid(),
    user_id text not null,
    conversation_id uuid references conversations(id) on delete cascade,
    topic text not null,
    questions jsonb not null,     -- includes expected_answer, never sent to client until graded
    submitted boolean default false,
    results jsonb,
    created_at timestamptz default now()
);

create index quiz_sessions_user_idx on quiz_sessions(user_id);
```

### Questions Structure

```json
[
  {
    "question": "What is the time complexity of bubble sort?",
    "expected_answer": "O(n²) in worst and average case..."
  }
]
```

### Results Structure

```json
[
  {
    "question": "What is the time complexity...",
    "expected_answer": "O(n²)...",
    "learner_answer": "O(n log n)",
    "correct": false,
    "feedback": "Bubble sort compares adjacent elements..."
  }
]
```

---

## Supabase Auth

Google OAuth via PKCE. User ID = `sub` claim from Supabase JWT.

```sql
-- No additional tables needed; uses auth.users
-- user_id in all tables = auth.users.id (text)
```

---

## Storage Bucket — `images`

Generated diagrams stored in Supabase Storage.

```sql
-- Bucket: images (Public)
-- Path pattern: {uuid}_{topic}.png
-- Public URL: https://xxx.supabase.co/storage/v1/object/public/images/{uuid}_{topic}.png
```

Create via Dashboard: Storage → Create bucket → Name: `images` → Public: ✅

---

## Row Level Security (Optional)

If enabling RLS, policies would be:

```sql
-- paper_chunks
create policy "Users see own chunks" on paper_chunks
for all using (user_id = auth.uid()::text);

-- conversations
create policy "Users see own conversations" on conversations
for all using (user_id = auth.uid()::text);

-- chat_messages
create policy "Users see own messages" on chat_messages
for all using (
    conversation_id in (select id from conversations where user_id = auth.uid()::text)
);

-- quiz_sessions
create policy "Users see own quizzes" on quiz_sessions
for all using (user_id = auth.uid()::text);
```