import { describe, test, expect, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, cleanup } from "@testing-library/react";
import userEvent from '@testing-library/user-event';
import { vi } from "vitest";
import { LoginPage } from "./LoginPage";

describe("LoginPage", () => {
    beforeEach(() => {
        vi.stubGlobal(
            "fetch",
            vi.fn(async () => {
                return new Response(
                    JSON.stringify({
                        status: "ok",
                    }),
                    { status: 200, headers: { "Content-Type": "application/json" } }
                );
            })
        );
    });
    afterEach(() => cleanup());

    test("login form exists", async () => {
        render(<LoginPage />);
        const loginInput = screen.getByTestId("email-login-input");
        const loginSubmit = screen.getByTestId("email-login-submit");
        expect(loginInput).toBeVisible();
        expect(loginSubmit).toBeVisible();
    });

    test("login form submit calls api", async () => {
        render(<LoginPage />);
        const loginInput = screen.getByTestId("email-login-input");
        const loginSubmit = screen.getByTestId("email-login-submit");
        const user = userEvent.setup();
        await user.type(loginInput, "test@example.com");
        await user.click(loginSubmit);
        await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/auth/magic-link", expect.objectContaining({
            method: "POST",
            body: JSON.stringify({ email: "test@example.com" })
        })))
    });

    test("login form submit returns sent message on success", async () => {
        render(<LoginPage />);
        const loginInput = screen.getByTestId("email-login-input");
        const loginSubmit = screen.getByTestId("email-login-submit");
        const user = userEvent.setup();
        await user.type(loginInput, "test@example.com");
        await user.click(loginSubmit);
        const sentMessage = await screen.findByTestId("email-sent-message");
        expect(sentMessage).toBeVisible()
    });

    test("login form submit returns failure message on failure", async () => {
        vi.stubGlobal("fetch", vi.fn(async () => new Response(
            JSON.stringify({ error: "Not found", code: "user_not_found" }),
            { status: 404, headers: { "Content-Type": "application/json" } }
        )));
        render(<LoginPage />);
        const loginInput = screen.getByTestId("email-login-input");
        const loginSubmit = screen.getByTestId("email-login-submit");
        const user = userEvent.setup();
        await user.type(loginInput, "test@example.com");
        await user.click(loginSubmit);
        const failedMessage = await screen.findByTestId("email-errored-message");
        expect(failedMessage).toBeVisible()
    });
});