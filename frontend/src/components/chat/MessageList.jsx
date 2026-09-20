import { useEffect, useRef } from "react";
import Message from "./Message";
import PhaseIndicator from "./PhaseIndicator";

export default function MessageList({ messages, phase }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, phase]);

  return (
    <main className="flex-1 overflow-y-auto px-6 py-6 space-y-4 max-w-3xl w-full mx-auto">
      {messages.length === 0 && !phase && (
        <div className="h-full flex items-center justify-center text-[var(--text-muted)] text-sm">
          Ask me to explain, research, or quiz you on a topic.
        </div>
      )}
      {messages.map((message, i) => (
        <Message key={i} message={message} />
      ))}
      {phase && <PhaseIndicator phase={phase} />}
      <div ref={bottomRef} />
    </main>
  );
}
