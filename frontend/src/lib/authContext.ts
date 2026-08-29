import { createContext } from "react";
import type { CurrentUser } from "./types";

/**
 * The context itself lives in its own file, separate from AuthProvider
 * (auth.tsx) and useAuth (useAuth.ts). Same Fast Refresh reasoning as the
 * other two splits: this file exports a value, not a component, so it can't
 * share a file with one.
 */

export type AuthState = {
  user: CurrentUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

export const AuthContext = createContext<AuthState | null>(null);
