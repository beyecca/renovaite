import { useEffect, useState } from "react";
import { isNamedError } from "./lib/errors";

type HealthzResponse = {
  status: string;
  service: string;
  git_sha: string;
  build_time: string;
};

type LoadState =
  | { state: "loading" }
  | { state: "ok"; data: HealthzResponse }
  | { state: "error"; message: string };

async function fetchJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(path, { signal });
  if (!res.ok) throw new Error(`${path} → HTTP ${res.status}`);
  return (await res.json()) as T;
}

function Row(props: { label: string; value: React.ReactNode }) {
  return (
    <div style={{ display: "flex", gap: 12, padding: "6px 0" }}>
      <div style={{ width: 120, color: "#555" }}>{props.label}</div>
      <div style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" }}>
        {props.value}
      </div>
    </div>
  );
}

export default function App() {
  const [health, setHealth] = useState<LoadState>({ state: "loading" });

  useEffect(() => {
    const controller = new AbortController();

    fetchJson<HealthzResponse>("/api/healthz", controller.signal)
      .then((data) => setHealth({ state: "ok", data }))
      .catch((e: unknown) => {
        if (isNamedError(e) && e.name === "AbortError") return;
        setHealth({ state: "error", message: e instanceof Error ? e.message : String(e) });
      });

    return () => controller.abort();
  }, []);

  return (
    <div
      style={{
        fontFamily: "system-ui",
        padding: 24,
        maxWidth: 900,
        margin: "0 auto",
      }}
    >
      <header style={{ marginBottom: 16 }}>
        <h1 style={{ margin: 0 }}>RenovAIte</h1>
        <p style={{ marginTop: 8, color: "#555" }}>
          Demo app for learning Django Ninja + React/TS + containers + AWS deploys.
        </p>
      </header>

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 12,
          padding: 16,
          background: "white",
        }}
      >
        <h2 style={{ marginTop: 0 }}>System Status</h2>

        {health.state === "loading" && <p>Loading API status…</p>}

        {health.state === "error" && (
          <>
            <p style={{ marginBottom: 8 }}>❌ API unreachable</p>
            <p style={{ margin: 0 }}>
              Error: <span style={{ fontFamily: "monospace" }}>{health.message}</span>
            </p>
          </>
        )}

        {health.state === "ok" && (
          <>
            <p style={{ marginBottom: 12 }}>
              ✅ API healthy (<code>{health.data.status}</code>)
            </p>

            <Row label="Service" value={health.data.service} />
            <Row label="Git SHA" value={health.data.git_sha} />
            <Row label="Build time" value={health.data.build_time} />

            <div style={{ marginTop: 12 }}>
              <a href="/api/healthz" target="_blank" rel="noreferrer">
                Open /api/healthz
              </a>
            </div>
          </>
        )}
      </div>

      <div style={{ marginTop: 16, color: "#666", fontSize: 14 }}>
        Tip: when you deploy, this page will show the SHA you just released.
      </div>
    </div>
  );
}
