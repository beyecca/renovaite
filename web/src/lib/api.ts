export async function fetchJson<T>(path: string, signal?: AbortSignal): Promise<T> {
    const res = await fetch(path, { signal });
    if (!res.ok) {
      throw new Error(`${path} → HTTP ${res.status}`);
    }
    return (await res.json()) as T;
  }
  