import { useAuth } from "../hooks/useAuth";
import { useChat } from "../hooks/useChat";
import { useConversations } from "../hooks/useConversation";
import TopBar from "../components/layout/TopBar";
import Sidebar from "../components/sidebar/Sidebar";
import MessageList from "../components/chat/MessageList";
import QuickActions from "../components/chat/QuickActions";
import ChatInput from "../components/chat/ChatInput";

const APP_NAME = "Learn Loop";

export default function ChatPage() {
  const { email, logout } = useAuth();
  const { conversations, refresh, loading, error } = useConversations();
  const {
    messages,
    phase,
    connected,
    reconnecting,
    conversationId,
    sendMessage,
    sendAction,
    startNewChat,
    loadConversation,
  } = useChat(refresh);

  return (
    <div className="h-screen flex flex-col bg-[var(--bg)]">
      <TopBar appName={APP_NAME} email={email} onLogout={logout} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          conversations={conversations}
          activeId={conversationId}
          onNewChat={startNewChat}
          onSelect={loadConversation}
          loading={loading}
          error={error}
          onRetry={refresh}
        />
        <div className="flex-1 flex flex-col overflow-hidden">
          {!connected && reconnecting && (
            <div className="px-4 py-2 text-center text-xs text-[var(--text-muted)] bg-[var(--surface)] border-b border-[var(--border)]">
              Reconnecting…
            </div>
          )}
          <MessageList messages={messages} phase={phase} />
          <QuickActions onAction={sendAction} disabled={!!phase || !connected} />
          <ChatInput onSend={sendMessage} disabled={!!phase || !connected} />
        </div>
      </div>
    </div>
  );
}