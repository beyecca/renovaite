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
    const responseBody = await res.json();
    if (res.ok) {
      return { ok: true, kind: "success", data: responseBody };
    } else {
      throw { status: res.status, code: responseBody.code, error: responseBody.error } as ApiError;
    }
  }
  catch (error) {
    if (status === undefined) {
      return { ok: false, kind: "network_error", error: "Something went wrong" };
    }
    else if (status >= 400 && status < 500) {
      return { ok: false, kind: "client_error", status: status, error: (error as ApiError).error, code: (error as ApiError).code }
    } else {
      return { ok: false, kind: "server_error", status: status!, error: (error as ApiError).error }
    }
  };
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