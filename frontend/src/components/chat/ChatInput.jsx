import { useState } from "react";
import VoiceRecorder from "../voice/VoiceRecorder";

export default function ChatInput({ onSend, onVoiceResult }) {
  const [input, setInput] = useState("");

  const handleSend = () => {
    onSend(input);
    setInput("");
  };

  return (
    <footer className="border-t border-slate-200 bg-white px-6 py-4">
      <div className="max-w-3xl mx-auto flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask to explain, research, or quiz you on a topic…"
          className="flex-1 border border-slate-300 rounded-lg px-4 py-2 text-sm"
        />
        <VoiceRecorder onResult={onVoiceResult} />
        <button
          onClick={handleSend}
          className="px-4 py-2 bg-slate-800 text-white rounded-lg text-sm"
        >
          Send
        </button>
      </div>
    </footer>
  );
}
