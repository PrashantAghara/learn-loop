export default function PhaseIndicator({ phase }) {
  if (!phase) return null;
  return (
    <div className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
      <span className="w-2 h-2 rounded-full bg-[var(--accent)] animate-pulse" />
      {phase.label}…
    </div>
  );
}
