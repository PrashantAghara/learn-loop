import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "./useAuth";
import client from "../api/client";

const WS_URL =
  import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/v1/ws/learn";
const MAX_RECONNECT_DELAY = 10000;

export function useChat(onConversationCreated) {
  const { token, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [phase, setPhase] = useState(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const manualCloseRef = useRef(false);

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      reconnectAttemptRef.current = 0;
    };

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
      } else if (data.type === "auth_error") {
        setPhase(null);
        logout();
        window.location.href = "/login";
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

    ws.onclose = () => {
      setConnected(false);
      if (manualCloseRef.current) return;
      const delay = Math.min(
        1000 * 2 ** reconnectAttemptRef.current,
        MAX_RECONNECT_DELAY
      );
      reconnectAttemptRef.current += 1;
      reconnectTimeoutRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => ws.close();

    wsRef.current = ws;
  }, [onConversationCreated, logout]);

  useEffect(() => {
    manualCloseRef.current = false;
    connect();
    return () => {
      manualCloseRef.current = true;
      clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback(
    (text) => {
      if (!text.trim() || wsRef.current?.readyState !== WebSocket.OPEN) return;
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
      if (wsRef.current?.readyState !== WebSocket.OPEN) return;
      wsRef.current.send(
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
    connected,
    conversationId,
    sendMessage,
    sendAction,
    startNewChat,
    loadConversation,
  };
}
