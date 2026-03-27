import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { request, authRequest, authPostJson } from "./api";
import { vi } from "vitest";


describe("api helper functions", () => {
    beforeEach(() => {
        localStorage.clear();
    });

    test('request returns ok true on success', async () => {
        vi.stubGlobal(
            "fetch",
            vi.fn(async () => {
                return new Response(
                    JSON.stringify({
                        status: "ok",
                        service: "api",
                        git_sha: "dev",
                        build_time: "now",
                    }),
                    { status: 200, headers: { "Content-Type": "application/json" } }
                );
            })
        );
        const response =  await request("test", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({test:"test"}),
        })
        expect(response).toEqual({ ok: true, kind: "success", data: { status: "ok", service: "api", git_sha: "dev", build_time: "now" } });
    });

    test('request returns ok false on client_error failure', async () => {
        const expectedResponse = { error: "Not found", code: "user_not_found" };
        vi.stubGlobal("fetch", vi.fn(async () => new Response(
            JSON.stringify(expectedResponse),
            { status: 404, headers: { "Content-Type": "application/json" } }
        )));
        const response =  await request("test", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({test:"test"}),
        })
        expect(response).toEqual({ ok: false, kind: "client_error", error: expectedResponse.error, code: expectedResponse.code, status: 404});
    });

    test('request returns ok false on server_error failure', async () => {
        const expectedResponse = { error: "Something went wrong", code: "internal_server_error" };
        vi.stubGlobal("fetch", vi.fn(async () => new Response(
            JSON.stringify(expectedResponse),
            { status: 500, headers: { "Content-Type": "application/json" } }
        )));
        const response =  await request("test", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({test:"test"}),
        })
        expect(response).toEqual({ ok: false, kind: "server_error", error: expectedResponse.error, status: 500 });
    });

    test('request returns ok false on network_error failure', async () => {
        const expectedResponse = { error: "Something went wrong", code: "network_error" };
        vi.stubGlobal("fetch", vi.fn(async () => Promise.reject(new Error('Network Error'))));
        const response =  await request("test", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({test:"test"}),
        })
        expect(response).toEqual({ ok: false, kind: "network_error", error: expectedResponse.error });
    });
});

describe("authRequest", () => {
    beforeEach(() => {
        localStorage.clear();
        vi.stubGlobal("fetch", vi.fn(async () =>
            new Response(JSON.stringify({ data: "ok" }), { status: 200, headers: { "Content-Type": "application/json" } })
        ));
    });
    afterEach(() => vi.unstubAllGlobals());

    test("injects Authorization header when token is present", async () => {
        localStorage.setItem("access_token", "my-token");
        await authRequest("/test");
        expect(fetch).toHaveBeenCalledWith("/test", expect.objectContaining({
            headers: expect.objectContaining({ Authorization: "Bearer my-token" }),
        }));
    });

    test("omits Authorization header when no token", async () => {
        await authRequest("/test");
        const [, options] = (fetch as ReturnType<typeof vi.fn>).mock.calls[0];
        expect(options.headers).not.toHaveProperty("Authorization");
    });

    test("dispatches auth:unauthorized event on 401", async () => {
        vi.stubGlobal("fetch", vi.fn(async () =>
            new Response(
                JSON.stringify({ error: "Unauthorized", code: "UNAUTHORIZED" }),
                { status: 401, headers: { "Content-Type": "application/json" } }
            )
        ));
        const listener = vi.fn();
        window.addEventListener("auth:unauthorized", listener);
        await authRequest("/test");
        expect(listener).toHaveBeenCalled();
        window.removeEventListener("auth:unauthorized", listener);
    });
});

describe("authPostJson", () => {
    beforeEach(() => {
        localStorage.clear();
        localStorage.setItem("access_token", "my-token");
        vi.stubGlobal("fetch", vi.fn(async () =>
            new Response(JSON.stringify({ data: "ok" }), { status: 200, headers: { "Content-Type": "application/json" } })
        ));
    });
    afterEach(() => vi.unstubAllGlobals());

    test("sends POST with JSON body and Authorization header", async () => {
        await authPostJson("/test", { key: "value" });
        expect(fetch).toHaveBeenCalledWith("/test", expect.objectContaining({
            method: "POST",
            body: JSON.stringify({ key: "value" }),
            headers: expect.objectContaining({
                "Content-Type": "application/json",
                Authorization: "Bearer my-token",
            }),
        }));
    });
});
