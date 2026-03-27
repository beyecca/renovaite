import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { postJson } from "../lib/api";
import { setTokens } from "../lib/auth";

type VerifyState =
    | { state: "verifying" }
    | { state: "error"; message: string };

export function VerifyPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const token = searchParams.get("token");
    const [verifyState, setVerifyState] = useState<VerifyState>(
        token ? { state: "verifying" } : { state: "error", message: "Missing token." }
    );

    useEffect(() => {
        if (!token) return;

        postJson<{ access: string; refresh: string }>("/api/auth/magic-link/verify", { token })
            .then((result) => {
                if (result.ok) {
                    setTokens(result.data.access, result.data.refresh);
                    navigate("/", { replace: true });
                } else {
                    setVerifyState({ state: "error", message: "Invalid or expired link." });
                }
            });
    }, [token, navigate]);

    if (verifyState.state === "verifying") {
        return <p data-testid="verify-loading">Verifying your link…</p>;
    }
    return <p data-testid="verify-error">{verifyState.message}</p>;
}
