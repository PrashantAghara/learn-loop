import NewChatButton from "./NewChatButton";
import ConversationItem from "./ConversationItem";

export default function Sidebar({
  conversations,
  activeId,
  onNewChat,
  onSelect,
  loading,
  error,
  onRetry,
}) {
  if (loading && conversations.length === 0) {
    return (
      <aside className="w-64 shrink-0 border-r border-[var(--border)] bg-[var(--surface)] flex items-center justify-center">
        <div className="text-[var(--text-muted)] text-sm">Loading conversations…</div>
      </aside>
    );
  }

  if (error && conversations.length === 0) {
    return (
      <aside className="w-64 shrink-0 border-r border-[var(--border)] bg-[var(--surface)] flex flex-col items-center justify-center p-4 gap-3">
        <div className="text-red-400 text-sm text-center">Failed to load conversations</div>
        <button
          onClick={onRetry}
          className="px-3 py-1.5 text-sm bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded transition"
        >
          Retry
        </button>
      </aside>
    );
  }

  return (
    <aside className="w-64 shrink-0 border-r border-[var(--border)] bg-[var(--surface)] flex flex-col p-3 gap-3">
      <NewChatButton onClick={onNewChat} />
      <div className="flex-1 overflow-y-auto flex flex-col gap-1">
        {conversations.map((c) => (
          <ConversationItem
            key={c.id}
            title={c.title}
            active={c.id === activeId}
            onClick={() => onSelect(c.id)}
          />
        ))}
        {conversations.length === 0 && !loading && (
          <div className="text-center text-[var(--text-muted)] text-sm py-4">
            No conversations yet. Start a new chat!
          </div>
        )}
      </div>
    </aside>
  );
}