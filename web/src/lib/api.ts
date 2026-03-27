import { getAccessToken } from "./auth";

export interface ApiError {
  status: number;
  code: string;
  error: string;
}

export type ApiResult<T> =
  | { ok: true; kind: "success", data: T }
  | { ok: false; kind: "client_error"; status: number; error: string; code: string }
  | { ok: false; kind: "server_error"; status: number; error: string }
  | { ok: false; kind: "network_error"; error: string }

export async function request<T>(path: string, options?: RequestInit): Promise<ApiResult<T>> {
  let status: number | undefined;
  try {
    const res = await fetch(path, options);
    status = res.status;

    let responseBody: unknown;
    try {
      responseBody = await res.json();
    } catch {
      return { ok: false, kind: "server_error", status: res.status, error: "Unexpected response format" };
    }

    if (res.ok) {
      return { ok: true, kind: "success", data: responseBody as T };
    } else {
      const body = responseBody as ApiError;
      if (status >= 400 && status < 500) {
        return { ok: false, kind: "client_error", status, error: body.error, code: body.code };
      }
      return { ok: false, kind: "server_error", status, error: body.error };
    }
  } catch {
    if (status === undefined) {
      return { ok: false, kind: "network_error", error: "Something went wrong" };
    }
    return { ok: false, kind: "server_error", status, error: "Something went wrong" };
  }
}


export async function authRequest<T>(path: string, options?: RequestInit): Promise<ApiResult<T>> {
  const token = getAccessToken();
  const result = await request<T>(path, {
    ...options,
    headers: {
      ...options?.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!result.ok && result.kind === "client_error" && result.status === 401) {
    // TODO: replace with router-aware navigation once a global auth context exists.
    // window.location.href causes a full page reload and execution continues after
    // this point — consumers may update unmounted state. Preferred fix: emit a custom
    // event that a top-level router listener handles, or accept an onUnauthorized callback.
    window.dispatchEvent(new CustomEvent("auth:unauthorized"));
    window.location.href = "/login";
  }
  return result;
}

export async function postJson<T>(path: string, body: unknown): Promise<ApiResult<T>> {
  return await request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
}

export async function authPostJson<T>(path: string, body: unknown): Promise<ApiResult<T>> {
  return authRequest<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}