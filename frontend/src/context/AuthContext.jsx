import { createContext, useState } from "react";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("access_token"));
  const [email, setEmail] = useState(localStorage.getItem("email"));

  const login = (newToken, userId, newEmail) => {
    localStorage.setItem("access_token", newToken);
    localStorage.setItem("user_id", userId);
    localStorage.setItem("email", newEmail);
    setToken(newToken);
    setEmail(newEmail);
  };

  const logout = () => {
    localStorage.clear();
    setToken(null);
    setEmail(null);
  };

  return (
    <AuthContext.Provider
      value={{ token, email, login, logout, isAuthenticated: !!token }}
    >
      {children}
    </AuthContext.Provider>
  );
}
