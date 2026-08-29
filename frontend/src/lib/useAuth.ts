import { useContext } from "react";
import { AuthContext } from "./authContext";

/**
 * Split from auth.tsx on purpose: that file needs to export the AuthProvider
 * component, and React Fast Refresh only hot-swaps files that export
 * components and nothing else. A hook living alongside a component in the
 * same file defeats that, same reasoning as lib/format.ts being split out
 * of PageHeader.tsx.
 */
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return ctx;
}
