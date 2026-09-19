import { API_BASE } from "../api/client";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center space-y-6 p-8 bg-white rounded-2xl shadow-md">
        <h1 className="text-3xl font-bold text-slate-800">Learn Loop</h1>
        <p className="text-slate-500">
          A self-learning research and tutoring agent
        </p>
        <button
          onClick={() =>
            (window.location.href = `${API_BASE}/auth/login/google`)
          }
          className="px-6 py-3 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  );
}
