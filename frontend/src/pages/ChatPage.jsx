import { useAuth } from "../hooks/useAuth";
import { useChat } from "../hooks/useChat";
import { useConversations } from "../hooks/useConversations";
import TopBar from "../components/layout/TopBar";
import Sidebar from "../components/sidebar/Sidebar";
import MessageList from "../components/chat/MessageList";
import QuickActions from "../components/chat/QuickActions";
import ChatInput from "../components/chat/ChatInput";

const APP_NAME = "Learn Loop";

export default function ChatPage() {
  const { email, logout } = useAuth();
  const { conversations, refresh } = useConversations();
  const {
    messages,
    phase,
    conversationId,
    sendMessage,
    sendAction,
    addVoiceResult,
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
        />
        <div className="flex-1 flex flex-col overflow-hidden">
          <MessageList messages={messages} phase={phase} />
          <QuickActions onAction={sendAction} disabled={!!phase} />
          <ChatInput
            onSend={sendMessage}
            onVoiceResult={addVoiceResult}
            disabled={!!phase}
          />
        </div>
      </div>
    </div>
  );
}
