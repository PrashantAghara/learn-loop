import { useAuth } from "../hooks/useAuth";
import { useChat } from "../hooks/useChat";
import ChatHeader from "../components/chat/ChatHeader";
import MessageList from "../components/chat/MessageList";
import ChatInput from "../components/chat/ChatInput";

export default function ChatPage() {
  const { email, logout } = useAuth();
  const { messages, loading, sendMessage, addVoiceResult } = useChat();

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <ChatHeader email={email} onLogout={logout} />
      <MessageList messages={messages} loading={loading} />
      <ChatInput onSend={sendMessage} onVoiceResult={addVoiceResult} />
    </div>
  );
}
