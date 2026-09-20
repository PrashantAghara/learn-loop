export default function NewChatButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-2 px-3 py-2 rounded-lg border border-[var(--border)] text-sm font-medium text-[var(--text)] hover:bg-[var(--surface-hover)] transition"
    >
      <span className="text-lg leading-none">+</span> New chat
    </button>
  );
}
