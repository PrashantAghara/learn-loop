export default function MessageBubble({ role, children }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl px-4 py-3 rounded-2xl whitespace-pre-wrap ${
          isUser
            ? "bg-slate-800 text-white"
            : "bg-white border border-slate-200 text-slate-800"
        }`}
      >
        {children}
      </div>
    </div>
  );
}
