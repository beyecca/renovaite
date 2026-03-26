import { describe, test, expect, beforeEach } from "vitest";
import { request } from "./api";
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