import { useCallback, useEffect, useState } from "react";
import client from "../api/client";

export function useConversations() {
  const [conversations, setConversations] = useState([]);

  const refresh = useCallback(async () => {
    const { data } = await client.get("/conversations");
    setConversations(data);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { conversations, refresh };
}
