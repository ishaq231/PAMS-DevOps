import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { Cityscape } from "../components/Cityscape";
import { useAuth } from "../lib/useAuth";
import { ApiError } from "../lib/api";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(username, password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      // The API returns 401 with a clear detail message for bad credentials;
      // anything else is worth showing verbatim rather than flattening to
      // "something went wrong", which tells the user nothing actionable.
      setError(
        err instanceof ApiError
          ? err.message
          : "Couldn't sign in. Try again.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      {/* Branding panel */}
      <div className="relative flex flex-col justify-center overflow-hidden bg-bg-darkest px-10 py-14 md:w-1/2 md:px-16">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-accent-dim text-2xl font-semibold text-bg-darkest">
            P
          </div>
          <div>
            <p className="text-xl font-semibold tracking-wide text-text-primary">
              PARAGON
            </p>
            <p className="text-xs tracking-[0.2em] text-text-secondary uppercase">
              Apartment Management
            </p>
          </div>
        </div>

        <h1 className="mt-12 max-w-md text-4xl leading-tight font-semibold text-text-primary">
          Every property, tenant, and payment in one place.
        </h1>
        <p className="mt-4 max-w-md text-text-secondary">
          Sign in to manage apartments, leases, maintenance, and finances across
          all Paragon locations.
        </p>

        <div className="pointer-events-none absolute inset-x-0 bottom-0">
          <Cityscape />
        </div>
      </div>

      {/* Form panel */}
      <div className="flex flex-1 items-center justify-center bg-bg-white px-6 py-14">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-semibold text-text-dark">Sign in</h2>
          <p className="mt-1 text-sm text-text-body">
            Use your Paragon account credentials.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-text-dark"
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1.5 h-11 w-full rounded-[10px] border border-border-light px-3 text-text-dark outline-none focus:border-accent focus:ring-2 focus:ring-accent/30"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-text-dark"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1.5 h-11 w-full rounded-[10px] border border-border-light px-3 text-text-dark outline-none focus:border-accent focus:ring-2 focus:ring-accent/30"
              />
            </div>

            {error && (
              <p
                role="alert"
                className="rounded-[10px] bg-danger/10 px-3 py-2 text-sm text-danger"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="h-11 w-full rounded-[10px] bg-accent font-semibold text-bg-darkest transition-colors hover:bg-accent-hover focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:outline-none disabled:opacity-60"
            >
              {submitting ? "Signing in…" : "Sign in"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
