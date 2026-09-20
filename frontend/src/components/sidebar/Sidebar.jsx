import NewChatButton from "./NewChatButton";
import ConversationItem from "./ConversationItem";

export default function Sidebar({
  conversations,
  activeId,
  onNewChat,
  onSelect,
}) {
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
      </div>
    </aside>
  );
}
