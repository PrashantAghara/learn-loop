import { useCallback, useEffect, useState } from "react";
import client, { withRetry } from "../api/client";

export function useConversations() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await withRetry(() => client.get("/conversations"));
      setConversations(data);
    } catch (err) {
      setError(err.message || "Failed to load conversations");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const { data } = await withRetry(() => client.get("/conversations"));
        if (mounted) setConversations(data);
      } catch (err) {
        if (mounted) setError(err.message || "Failed to load conversations");
      } finally {
        if (mounted) setLoading(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, [refresh]);

  return { conversations, refresh, loading, error };
}