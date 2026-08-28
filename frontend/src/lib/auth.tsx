import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  api,
  clearToken,
  getToken,
  setToken,
  setUnauthorizedHandler,
} from "./api";
import type { CurrentUser, LoginResponse } from "./types";

/**
 * React Context is how a value gets shared across the whole component tree
 * without passing it down through every level as props. Login state is needed
 * by the sidebar, the header, and every protected page, so it belongs here
 * rather than being threaded through a dozen components.
 */

type AuthState = {
  user: CurrentUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  // Starts true because on a page refresh we hold a token but don't yet know
  // if it's still valid. Rendering routes before that check finishes would
  // briefly bounce a logged-in user to the login screen.
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  useEffect(() => {
    // Lets api.ts trigger a logout when any request comes back 401.
    setUnauthorizedHandler(() => {
      clearToken();
      setUser(null);
    });
  }, []);

  useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    // We could decode the JWT locally, but asking the server is the honest
    // check: it verifies the signature and the expiry rather than trusting
    // whatever happens to be sitting in localStorage.
    api
      .get<CurrentUser>("/me")
      .then(setUser)
      .catch(() => {
        clearToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const data = await api.post<LoginResponse>("/login", {
      username,
      password,
    });
    setToken(data.access_token);
    setUser(data.user);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return ctx;
}
