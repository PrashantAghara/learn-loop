import { API_BASE } from "../api/client";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg)]">
      <div className="text-center space-y-6 p-10 bg-[var(--surface)] border border-[var(--border)] rounded-2xl shadow-xl">
        <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-indigo-400 to-violet-600" />
        <h1 className="text-3xl font-bold text-[var(--text)]">Learn Loop</h1>
        <p className="text-[var(--text-muted)]">
          A self-learning research and tutoring agent
        </p>
        <button
          onClick={() =>
            (window.location.href = `${API_BASE}/auth/login/google`)
          }
          className="px-6 py-3 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg transition"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
