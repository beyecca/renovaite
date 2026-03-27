import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import { vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router";
import { VerifyPage } from "./VerifyPage";

const mockNavigate = vi.fn();
vi.mock("react-router", async (importOriginal) => {
    const actual = await importOriginal<typeof import("react-router")>();
    return { ...actual, useNavigate: () => mockNavigate };
});

function renderWithToken(token?: string) {
    const url = token ? `/auth/verify?token=${token}` : "/auth/verify";
    return render(
        <MemoryRouter initialEntries={[url]}>
            <Routes>
                <Route path="/auth/verify" element={<VerifyPage />} />
            </Routes>
        </MemoryRouter>
    );
}

describe("VerifyPage", () => {
    beforeEach(() => {
        mockNavigate.mockReset();
        localStorage.clear();
        vi.stubGlobal(
            "fetch",
            vi.fn(async () =>
                new Response(
                    JSON.stringify({ access: "access-tok", refresh: "refresh-tok" }),
                    { status: 200, headers: { "Content-Type": "application/json" } }
                )
            )
        );
    });
    afterEach(() => cleanup());

    test("shows loading state while verifying", () => {
        renderWithToken("some-token");
        expect(screen.getByTestId("verify-loading")).toBeVisible();
    });

    test("navigates home and stores tokens on success", async () => {
        renderWithToken("valid-token");
        await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/", { replace: true }));
        expect(localStorage.getItem("access_token")).toBe("access-tok");
        expect(localStorage.getItem("refresh_token")).toBe("refresh-tok");
    });

    test("shows error message on invalid or expired token", async () => {
        vi.stubGlobal(
            "fetch",
            vi.fn(async () =>
                new Response(
                    JSON.stringify({ error: "Invalid or expired token.", code: "UNAUTHORIZED" }),
                    { status: 401, headers: { "Content-Type": "application/json" } }
                )
            )
        );
        renderWithToken("bad-token");
        const error = await screen.findByTestId("verify-error");
        expect(error).toBeVisible();
        expect(error.textContent).toBe("Invalid or expired link.");
    });

    test("shows error immediately if no token in URL", () => {
        renderWithToken();
        const error = screen.getByTestId("verify-error");
        expect(error).toBeVisible();
        expect(error.textContent).toBe("Missing token.");
        expect(fetch).not.toHaveBeenCalled();
    });
});
