import { useCallback, useMemo, useState } from "react";
import { AuthContext } from "./AuthContext";

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const [email, setEmail] = useState(localStorage.getItem("email"));

  const login = useCallback((newToken, userId, newEmail) => {
    localStorage.setItem("access_token", newToken);
    localStorage.setItem("user_id", userId);
    localStorage.setItem("email", newEmail);
    setToken(newToken);
    setEmail(newEmail);
  }, []);

  const logout = useCallback(() => {
    localStorage.clear();
    setToken(null);
    setEmail(null);
  }, []);

  const value = useMemo(
    () => ({ token, email, login, logout, isAuthenticated: !!token }),
    [token, email, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}