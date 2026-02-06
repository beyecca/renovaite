import { useEffect, useState } from "react";
import { fetchJson } from "../lib/api";
import type { HealthzResponse } from "../types/api";
import { isNamedError } from "../lib/errors";

type LoadState =
  | { state: "loading" }
  | { state: "ok"; data: HealthzResponse }
  | { state: "error"; message: string };

export function LandingPage() {
  const [health, setHealth] = useState<LoadState>({ state: "loading" });

  useEffect(() => {
    const controller = new AbortController();

    async function run() {
      try {
        const data = await fetchJson<HealthzResponse>("/api/healthz", controller.signal);
        setHealth({ state: "ok", data });
      } catch (e: unknown) {
        if (isNamedError(e) && e.name === "AbortError") return;
        setHealth({ state: "error", message: (e as Error).message });
      }
    }

    run();
    return () => controller.abort();
  }, []);

  return (
    <div style={{ fontFamily: "system-ui", padding: 24, maxWidth: 960, margin: "0 auto" }}>
      <header style={{ marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>RenoBrain</h1>
        <p style={{ marginTop: 8, color: "#555" }}>
          A small demo app for learning Django Ninja + React/TS + containers + AWS deploys.
        </p>
      </header>

      <section
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 16,
          background: "white",
        }}
      >
        <h2 style={{ marginTop: 0 }}>System Status</h2>

        {health.state === "loading" && <div>Checking API…</div>}

        {health.state === "error" && (
          <div>
            ❌ API unavailable — <span style={{ fontFamily: "monospace" }}>{health.message}</span>
          </div>
        )}

        {health.state === "ok" && (
          <>
            <div>✅ API healthy</div>
            <div style={{ marginTop: 12, display: "grid", gap: 6 }}>
              <div>
                <strong>Service:</strong> <code>{health.data.service}</code>
              </div>
              <div>
                <strong>Status:</strong> <code>{health.data.status}</code>
              </div>
              <div>
                <strong>Git SHA:</strong> <code>{health.data.git_sha}</code>
              </div>
              <div>
                <strong>Build time:</strong> <code>{health.data.build_time}</code>
              </div>
            </div>
          </>
        )}
      </section>

      <section style={{ marginTop: 16 }}>
        <a href="/api/healthz" target="_blank" rel="noreferrer">
          Open /api/healthz
        </a>
      </section>
    </div>
  );
}
