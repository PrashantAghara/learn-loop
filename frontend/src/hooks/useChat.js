import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "./useAuth";
import client, { withRetry } from "../api/client";

const WS_URL =
  import.meta.env.VITE_WS_URL || "ws://localhost:8000/api/v1/ws/learn";
const MAX_RECONNECT_DELAY = 10000;

export function useChat(onConversationCreated) {
  const { logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [phase, setPhase] = useState(null);
  const [connected, setConnected] = useState(false);
  const [reconnecting, setReconnecting] = useState(false);
  const wsRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const manualCloseRef = useRef(false);
  const connectRef = useRef(null);

  const getToken = useCallback(() => localStorage.getItem("access_token"), []);

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      setReconnecting(false);
      reconnectAttemptRef.current = 0;
    };

    ws.onmessage = (e) => {
      try {
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
              error: true,
            },
          ]);
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      if (manualCloseRef.current) return;
      setReconnecting(true);
      const delay = Math.min(
        1000 * 2 ** reconnectAttemptRef.current,
        MAX_RECONNECT_DELAY
      );
      reconnectAttemptRef.current += 1;
      reconnectTimeoutRef.current = setTimeout(() => {
        if (!manualCloseRef.current) connectRef.current?.();
      }, delay);
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
      ws.close();
    };

    wsRef.current = ws;
  }, [onConversationCreated, logout]);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

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
      const token = getToken();
      if (!token) {
        logout();
        window.location.href = "/login";
        return;
      }
      setMessages((prev) => [...prev, { role: "user", content: text }]);
      wsRef.current.send(
        JSON.stringify({
          token,
          conversation_id: conversationId,
          message: text,
        })
      );
    },
    [conversationId, getToken, logout]
  );

  const sendAction = useCallback(
    (action) => {
      if (wsRef.current?.readyState !== WebSocket.OPEN) return;
      const token = getToken();
      if (!token) {
        logout();
        window.location.href = "/login";
        return;
      }
      wsRef.current.send(
        JSON.stringify({
          type: "action",
          action,
          token,
          conversation_id: conversationId,
        })
      );
    },
    [conversationId, getToken, logout]
  );

  const startNewChat = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setPhase(null);
  }, []);

  const loadConversation = useCallback(async (id) => {
    try {
      const { data } = await withRetry(() => client.get(`/conversations/${id}/messages`));
      setConversationId(id);
      setPhase(null);
      setMessages(
        data.messages.map((m) => ({
          role: m.role,
          content: m.role === "user" ? m.content : undefined,
          response: m.role === "assistant" ? m.content : undefined,
          ...(m.metadata || {}),
        }))
      );
    } catch (err) {
      console.error("Failed to load conversation:", err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", response: "Failed to load conversation. Please try again.", error: true },
      ]);
    }
  }, []);

  return {
    messages,
    phase,
    connected,
    reconnecting,
    conversationId,
    sendMessage,
    sendAction,
    startNewChat,
    loadConversation,
  };
}