import { useState } from "react";

export default function ChatInput({ onSend, disabled }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface)] px-6 py-4">
      <div className="max-w-3xl mx-auto flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={disabled}
          placeholder="Ask to explain, research, or quiz you on a topic…"
          className="flex-1 border border-[var(--border)] bg-[var(--bg)] text-[var(--text)] rounded-lg px-4 py-2 text-sm outline-none focus:border-[var(--accent)] disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={disabled}
          className="px-4 py-2 bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white rounded-lg text-sm disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </footer>
  );
}
