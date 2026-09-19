export default function ChatHeader({ email, onLogout }) {
  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4 flex justify-between items-center">
      <h1 className="text-xl font-bold text-slate-800">Learn Loop</h1>
      <div className="flex items-center gap-3 text-sm text-slate-500">
        <span>{email}</span>
        <button
          onClick={onLogout}
          className="text-slate-400 hover:text-slate-600"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
