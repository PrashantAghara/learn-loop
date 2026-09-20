import ThemeToggle from "./ThemeToggle";

export default function TopBar({ appName, email, onLogout }) {
  return (
    <header className="h-14 flex items-center justify-between px-4 border-b border-[var(--border)] bg-[var(--surface)]">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-md bg-gradient-to-br from-indigo-400 to-violet-600" />
        <span className="font-semibold text-[var(--text)]">{appName}</span>
      </div>
      <div className="flex items-center gap-3">
        <ThemeToggle />
        <span className="text-sm text-[var(--text-muted)] hidden sm:inline">
          {email}
        </span>
        <button
          onClick={onLogout}
          className="text-sm text-[var(--text-muted)] hover:text-[var(--text)]"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
