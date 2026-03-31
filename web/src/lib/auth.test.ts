import { describe, test, expect, beforeEach } from "vitest";
import { setTokens, getAccessToken, getRefreshToken, clearTokens } from "./auth";


describe("auth tokens", () => {
    beforeEach(() => {
        localStorage.clear();
    });

    test('setTokens adds token to localStorage', () => {
        const expected_access = "test";
        const expected_refresh = "twice";
        setTokens(expected_access, expected_refresh)
        const actual_access = getAccessToken();
        const actual_refresh = getRefreshToken();
        expect(actual_access).toBe(expected_access);
        expect(actual_refresh).toBe(expected_refresh);
    });

    test('getAccessToken returns null when not set', () => {
        expect(getAccessToken()).toBeNull();
    });

    test('getRefreshToken returns null when not set', () => {
        expect(getRefreshToken()).toBeNull();
    });

    test('clearTokens removes tokens from localStorage', () => {
        const expected_access = "test";
        const expected_refresh = "twice";
        setTokens(expected_access, expected_refresh)

        expect(getAccessToken()).toBe(expected_access);
        expect(getRefreshToken()).toBe(expected_refresh);

        clearTokens();

        expect(getAccessToken()).toBeNull();
        expect(getRefreshToken()).toBeNull();
    });
});