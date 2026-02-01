import { useEffect, useState } from "react";

type Health = { status: string };

export default function App() {
  const [data, setData] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/healthz")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<Health>;
      })
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <div style={{ fontFamily: "system-ui", padding: 24 }}>
      <h1>RenoBrain</h1>

      {error && <p>API error: {error}</p>}
      {!error && !data && <p>Loading API status…</p>}
      {data && <p>API status: {data.status}</p>}
    </div>
  );
}
