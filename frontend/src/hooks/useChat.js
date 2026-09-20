import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "./useAuth";
import client from "../api/client";

const WS_URL = "ws://localhost:8000/api/v1/ws/learn";

export function useChat(onConversationCreated) {
  const { token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [phase, setPhase] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket(WS_URL);
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "phase") {
        setPhase({ phase: data.phase, label: data.label });
      } else if (data.type === "conversation_created") {
        setConversationId(data.conversation_id);
        onConversationCreated?.();
      } else if (data.type === "result") {
        setPhase(null);
        setConversationId(data.conversation_id);
        setMessages((prev) => [...prev, { role: "assistant", ...data }]);
      } else if (data.type === "error") {
        setPhase(null);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            response: data.detail || "Something went wrong.",
          },
        ]);
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  const sendMessage = useCallback(
    (text) => {
      if (!text.trim() || !wsRef.current) return;
      setMessages((prev) => [...prev, { role: "user", content: text }]);
      wsRef.current.send(
        JSON.stringify({
          token,
          conversation_id: conversationId,
          message: text,
        })
      );
    },
    [token, conversationId]
  );

  const sendAction = useCallback(
    (action) => {
      wsRef.current?.send(
        JSON.stringify({
          type: "action",
          action,
          token,
          conversation_id: conversationId,
        })
      );
    },
    [token, conversationId]
  );

  const addVoiceResult = useCallback((data) => {
    setMessages((prev) => [
      ...prev,
      { role: "user", content: data.transcribed_question },
      { role: "assistant", ...data },
    ]);
  }, []);

  const startNewChat = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setPhase(null);
  }, []);

  const loadConversation = useCallback(async (id) => {
    const { data } = await client.get(`/conversations/${id}/messages`);
    setConversationId(id);
    setPhase(null);
    setMessages(
      data.map((m) => ({
        role: m.role,
        content: m.role === "user" ? m.content : undefined,
        response: m.role === "assistant" ? m.content : undefined,
        ...(m.metadata || {}),
      }))
    );
  }, []);

  return {
    messages,
    phase,
    conversationId,
    sendMessage,
    sendAction,
    addVoiceResult,
    startNewChat,
    loadConversation,
  };
}
