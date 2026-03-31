---
name: open-pr
description: Opens a GitHub PR for the current branch. Diffs against main, generates a title and summary from the changeset, and runs gh pr create. Invoke after pushing by saying "open a PR".
tools: Bash, Read, Glob, Grep
---

You are opening a GitHub pull request for the current Renovaite branch.

**Steps:**

1. Run `git rev-parse --abbrev-ref HEAD` to get the current branch name.
2. Run `git diff main...HEAD` to understand all changes in this branch.
3. Run `git log main...HEAD --oneline` to see the commit history.
4. Run `git diff main...HEAD --stat` to see which files changed.
5. Derive the following from the above:
   - **PR title** — short (under 70 chars), imperative tense, describes what the PR does (e.g. "Add JWT auth and magic link login flow")
   - **Summary** — 3–5 bullet points covering what changed and why. Group by area (backend / frontend / tests) if the change spans multiple layers.
   - **Test plan** — bulleted checklist of what to verify when reviewing (e.g. "POST /auth/magic-link returns 200 with valid email", "401 returned when no token provided")
   - **Notion task reference** — extract the PRD/task reference from the branch name (e.g. `prd1/feat-auth-setup` → PRD 1) and include it as plain text (e.g. "PRD 1")
6. Run `gh pr create` with the generated title and body. Use this body format:

```
## Summary
- <bullet>
- <bullet>

## Test plan
- [ ] <item>
- [ ] <item>

## Related
<prd-reference>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

7. Return the PR URL to the user.

**Rules:**
- Base branch is always `main`
- Do not ask for confirmation — generate and create the PR in one shot
- If `gh` is not authenticated, tell the user to run `gh auth login` and stop
- If the branch has no commits ahead of main, tell the user and stop
