import { useState } from "react";

export default function ChatInput({ onSend, disabled }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input);
    setInput("");
  };

  return (
    <div className="px-6 pb-6 pt-2">
      <div className="max-w-3xl mx-auto flex items-center gap-2 bg-[var(--surface)] border border-[var(--border)] rounded-2xl px-4 py-3 shadow-sm focus-within:border-[var(--accent)] transition">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={disabled}
          placeholder="Ask to explain, research, or quiz you on a topic…"
          className="flex-1 bg-transparent text-[var(--text)] text-sm outline-none disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={disabled}
          aria-label="Send"
          className="w-8 h-8 flex items-center justify-center rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white disabled:opacity-40 transition"
        >
          ↑
        </button>
      </div>
    </div>
  );
}
