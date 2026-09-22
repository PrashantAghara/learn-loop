import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MessageBubble({ role, children }) {
  const isUser = role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-xl px-4 py-2.5 rounded-2xl bg-[var(--accent)] text-white text-sm leading-relaxed whitespace-pre-wrap">
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className="prose-chat text-[var(--text)] text-[15px] leading-7">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  );
}
