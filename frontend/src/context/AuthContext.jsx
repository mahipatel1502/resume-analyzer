import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { loginUser, signupUser } from "../api/endpoints";

const AuthContext = createContext(null);
const TOKEN_KEY = "ra_token";
const USER_KEY = "ra_user";

function readStoredUser() {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
  });
  const [user, setUser] = useState(() => readStoredUser());
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    setIsReady(true);
  }, []);

  useEffect(() => {
    if (!isReady || typeof window === "undefined") return;
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  }, [isReady, token]);

  useEffect(() => {
    if (!isReady || typeof window === "undefined") return;
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }, [isReady, user]);

  const persistAuth = useCallback((authData) => {
    setToken(authData.access_token);
    setUser(authData.user);
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, authData.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(authData.user));
    }
  }, []);

  const login = useCallback(async (credentials) => {
    const authData = await loginUser(credentials);
    persistAuth(authData);
    return authData;
  }, [persistAuth]);

  const signup = useCallback(async (credentials) => {
    const authData = await signupUser(credentials);
    persistAuth(authData);
    return authData;
  }, [persistAuth]);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      isReady,
      login,
      signup,
      logout,
    }),
    [token, user, isReady, login, signup, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}