import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageBubble({ role, children }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-[var(--accent)] text-white whitespace-pre-wrap"
            : "bg-[var(--surface)] border border-[var(--border)] text-[var(--text)]"
        }`}
      >
        {isUser ? (
          children
        ) : (
          <div className="prose-chat">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {children}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
