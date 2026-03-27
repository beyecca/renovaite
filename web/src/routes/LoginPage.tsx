import { useState } from "react";
import { postJson } from "../lib/api";

type FormState =
    | { "state": "idle" }
    | { "state": "loading" }
    | { "state": "sent" }
    | { "state": "error"; "message": string };

export function LoginPage() {
    const [email, setEmail] = useState("");
    const [formState, setFormState] = useState<FormState>({ "state": "idle" });
    async function handleSubmit(formData: FormData) {
        // TODO: rename to submittedEmail to avoid shadowing the outer email state variable.
        const email = formData.get("email") as string;
        setEmail(email);
        setFormState({ state: "loading" });
        const resp = await postJson("/api/auth/magic-link", { email });
        if (resp.ok) {
            setFormState({ state: "sent" });
        } else {
            setFormState({ state: "error", message: "Something went wrong. Please try again." });
        }
    }
    function renderContent() {
        switch (formState.state) {
            case "sent":
                return <p data-testid="email-sent-message">{`If an account exists for ${email}, you'll receive an email to log in!`}</p>
            case "error":
                return <p data-testid="email-errored-message">{formState.message}</p>
            default: // idle + loading
                return <>
                    <label htmlFor="email-login-input">Email</label>
                    <input id="email-login-input" name="email" type="email" data-testid="email-login-input" />
                    <button type="submit" disabled={formState.state === "loading"} data-testid="email-login-submit">Send magic link</button>
                </>
        }
    }
    return (<form onSubmit={(e) => {
        e.preventDefault();
        handleSubmit(new FormData(e.currentTarget));
    }}>
        {renderContent()}
    </form>);
}