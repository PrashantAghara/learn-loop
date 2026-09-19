import { useEffect, useRef } from "react";
import Message from "./Message";

export default function MessageList({ messages, loading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <main className="flex-1 overflow-y-auto px-6 py-6 space-y-4 max-w-3xl w-full mx-auto">
      {messages.map((message, i) => (
        <Message key={i} message={message} />
      ))}
      {loading && <p className="text-slate-400 text-sm">Thinking…</p>}
      <div ref={bottomRef} />
    </main>
  );
}
