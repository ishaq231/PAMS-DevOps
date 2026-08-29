import {
  useCallback,
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
import { AuthContext } from "./authContext";

/**
 * React Context is how a value gets shared across the whole component tree
 * without passing it down through every level as props. Login state is needed
 * by the sidebar, the header, and every protected page, so it belongs here
 * rather than being threaded through a dozen components.
 *
 * This file exports only the AuthProvider component. The context itself
 * (authContext.ts) and the useAuth hook (useAuth.ts) are deliberately in
 * separate files — see the note in either for why.
 */

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  // True only when a token actually exists to verify. Computing this from
  // getToken() up front — rather than starting true and setting it false in
  // an effect — means there's nothing to correct after the first render when
  // there's no token: we already know synchronously there's nothing to check.
  const [loading, setLoading] = useState(() => Boolean(getToken()));

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
      // loading's initial value already accounts for this case — nothing to do.
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
