# Known Limitations

## 1. Render Free Tier Cold Starts

**Issue:** No traffic for 15 minutes → service spins down. Next request pays ~30s startup cost.

**Impact:** First request after idle period is slow.

**Mitigation:** Not suitable for production SLA. For demo/portfolio use only. Upgrade to paid Render plan for always-on.

---

## 2. Live Web Results Not Persisted

**Issue:** Tavily search results ground the immediate answer but **aren't stored in pgvector**.

**Impact:** Repeat questions about the same topic won't benefit from prior live-web research. Only the four structured sources (arXiv, OpenAlex, Semantic Scholar, Wikipedia) build lasting RAG coverage.

**Design Decision:** Tavily results lack stable "paper" identity (no DOI, no persistent URL) → can't reliably deduplicate or cite.

---

## 3. Tool-Calling Reliability Ceiling

**Issue:** Groq's `gpt-oss-120b` has documented tool-calling reliability issues (current generation, not project-specific).

**Impact:** The Research Agent (tool-calling ReAct) occasionally fails to call tools correctly or generates malformed calls.

**Mitigation:** **Auto-Research** (`auto_research_node`) — deterministic fallback that calls all five sources directly. Used automatically whenever `explain`/`assess` hit a topic with no RAG coverage. The tool-calling agent is only used for explicit *"research X"* user requests.

---

## 4. Embedding Model Fixed

**Issue:** Uses `sentence-transformers/all-MiniLM-L6-v2` (384-dim) via HuggingFace Inference API.

**Impact:** Cannot change embedding dimension without re-ingesting all chunks. 384-dim is a trade-off: smaller index, faster search, but less semantic resolution than 768/1024/1536-dim models.

**Why:** Moved off local `sentence-transformers` + PyTorch specifically to fit Render free-tier memory limit (512MB). Local model + PyTorch ≈ 400MB+ just for embeddings.

---

## 5. Single-User RAG Scope

**Issue:** `paper_chunks` are scoped per `user_id`. Research is **not shared** across accounts.

**Impact:** Two users asking about the same topic will each trigger independent research + ingestion. No cross-user knowledge reuse.

**Design Decision:** Privacy-first. Users may research proprietary/internal topics. Sharing would require explicit opt-in + deduplication logic.

---

## 6. Image Generation Reliability

**Issue:** Pollinations.ai is free, keyless, but:
- No SLA
- Occasional timeouts/failures
- No control over style/quality
- Rate limits undocumented

**Mitigation:** `fetch_generated_image` returns `None` on failure → Explainer continues without diagram. Frontend handles missing `image_path` gracefully.

---

## 7. Quiz Grading Subjectivity

**Issue:** LLM-as-judge grading (`grade_answer`) is not deterministic.

**Impact:** Same answer may get different `correct`/`feedback` on re-grade. No exact-match or rubric-based scoring.

**Mitigation:** Prompt explicitly instructs consistency. For production, consider fine-tuned grader or rule-based extraction for factual Qs.

---

## 8. No Conversation Branching

**Issue:** Conversations are linear. No "fork from message N" or "compare two threads."

**Impact:** Can't explore alternative explanations side-by-side.

---

## 9. No Offline/Export

**Issue:** No export of conversations, quizzes, or personal memory (mem0).

**Impact:** Data locked in platform.

---

## 10. WebSocket Reconnection

**Issue:** Frontend implements reconnect with exponential backoff, but:
- No message deduplication on reconnect
- In-flight requests may be lost
- No "last seen phase" resume

**Mitigation:** REST fallback (`/learn/message`) exists for critical paths.