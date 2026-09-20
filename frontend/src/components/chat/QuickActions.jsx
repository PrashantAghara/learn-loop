const ACTIONS = [
  { key: "continue_research", label: "🔎 Continue research" },
  { key: "quiz_context", label: "📝 Quiz me on this" },
  { key: "explain_related", label: "💡 Explain a related concept" },
];

export default function QuickActions({ onAction, disabled }) {
  return (
    <div className="flex gap-2 flex-wrap px-6 pb-2 max-w-3xl mx-auto w-full">
      {ACTIONS.map((a) => (
        <button
          key={a.key}
          disabled={disabled}
          onClick={() => onAction(a.key)}
          className="text-xs px-3 py-1.5 rounded-full border border-[var(--border)] text-[var(--text-muted)] hover:bg-[var(--surface-hover)] disabled:opacity-40 transition"
        >
          {a.label}
        </button>
      ))}
    </div>
  );
}
