import { useState } from "react";
import client from "../api/client";

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const addMessage = (message) => setMessages((prev) => [...prev, message]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    addMessage({ role: "user", content: text });
    setLoading(true);
    try {
      const { data } = await client.post("/learn/message", { message: text });
      addMessage({ role: "assistant", ...data });
    } catch {
      addMessage({
        role: "assistant",
        response: "Something went wrong — try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const addVoiceResult = (data) => {
    addMessage({ role: "user", content: data.transcribed_question });
    addMessage({ role: "assistant", ...data });
  };

  return { messages, loading, sendMessage, addVoiceResult };
}
