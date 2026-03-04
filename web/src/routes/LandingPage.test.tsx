import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { LandingPage } from "./LandingPage";
import type { NamedError } from "../lib/errors";

describe("LandingPage", () => {
  it("shows healthy status when API returns ok", async () => {
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

    render(<LandingPage />);

    expect(await screen.findByText(/API healthy/i)).not.toBeNull();
  });

  it("shows error when API fails", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => {
      return new Response("nope", { status: 500 });
    }) as NamedError);

    render(<LandingPage />);

    expect(await screen.findByText(/API unavailable/i)).not.toBeNull();
  });
});
