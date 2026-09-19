import { useState } from "react";
import client from "../../api/client";

const OPTIONS = [
  "Got it",
  "Too basic",
  "Use an analogy",
  "I already know this",
];

export default function ReactionBar({ topic }) {
  const [sent, setSent] = useState(false);

  const sendReaction = async (reaction) => {
    await client.post("/learn/reaction", { topic, reaction });
    setSent(true);
  };

  if (sent)
    return <p className="text-xs text-slate-400 mt-2">Reaction recorded</p>;

  return (
    <div className="flex gap-2 mt-2 flex-wrap">
      {OPTIONS.map((opt) => (
        <button
          key={opt}
          onClick={() => sendReaction(opt)}
          className="text-xs px-3 py-1 border border-slate-300 rounded-full hover:bg-slate-100"
        >
          {opt}
        </button>
      ))}
    </div>
  );
}
