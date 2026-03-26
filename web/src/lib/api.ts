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

export async function fetchJson<T>(path: string, options?: RequestInit): Promise<ApiResult<T>> {
  return request(path, options);
}


export async function postJson<T>(path: string, body: unknown): Promise<ApiResult<T>> {
  return await request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
}