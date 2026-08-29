import { useCallback, useEffect, useState } from "react";
import { ApiError } from "./api";

/**
 * Every data screen needs the same three states: loading, error, and data.
 * Writing that by hand in each page means three useStates and a try/catch
 * repeated a dozen times, and it's exactly the kind of repetition where one
 * screen quietly forgets its error handling and renders blank instead.
 *
 * `deps` works like useEffect's dependency array — pass [tenantId] and the
 * request re-runs when the id changes.
 */
export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
): {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
} {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  useEffect(() => {
    // If the component unmounts mid-request, setting state afterwards is a
    // React warning and a small memory leak, so we drop the result instead.
    let cancelled = false;

    // This is React's own documented pattern for fetching in an effect
    // (react.dev, "You Might Not Need an Effect" — the person-bio example
    // resets state the same way before the fetch starts). It's disabled here
    // deliberately, not as a blanket suppression: unlike the loading flag in
    // auth.tsx, this effect re-runs on every dependency change and every
    // reload(), so there's no one-time initial value that could replace it —
    // the reset genuinely has to happen again on each run.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);

    fetcher()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (cancelled) return;
        // A 401 is already handled globally in api.ts (it logs the user out),
        // so there's no point showing an error box that's about to unmount.
        if (err instanceof ApiError && err.status === 401) return;
        setError(
          err instanceof Error ? err.message : "Something went wrong.",
        );
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  return { data, loading, error, reload };
}
