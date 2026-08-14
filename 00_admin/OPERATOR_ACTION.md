# OPERATOR ACTION REQUIRED

## OA-1 — `agy` authentication expired (raised 2026-08-14, Audit 1)

**Status: run CONTINUES in degraded audit mode. Not blocking.**

### What happened
`agy` was dispatched for Audit 1 and returned:

```
Authentication required. Please visit the URL to log in:
  https://accounts.google.com/o/oauth2/auth?...&redirect_uri=https%3A%2F%2Fantigravity.google%2Foauth-callback...
Waiting for authentication (timeout 60s)...
Error: authentication timed out.
```

`agy` requires an **interactive Google OAuth login**. This session has no browser and cannot
complete the flow, so the credential is one the environment does not hold — standing order **S3.2**.

Note `agy` worked earlier today during the gap-discovery run, so the token has expired since;
this is not a misconfiguration.

### Why the run was not halted
S3 halts exist to prevent unsafe or futile work. Here only **one of two** auditors is unavailable:
**Codex remains functional** and was dispatched successfully for Audit 1. Halting all execution
because a second opinion is temporarily unavailable would waste the provisioned environment and the
verified LAMMPS/OpenFOAM build for no safety gain.

**Degradation is recorded honestly rather than hidden:** Audits taken while `agy` is unavailable
have **one auditor, not two**, and therefore cannot satisfy the audit protocol's
reviewer-vs-reviewer disagreement requirement. Every such audit is tagged
`SINGLE-AUDITOR — DEGRADED` in `DECISIONS.md`, and the physics-and-modelling perspective (agy's
assigned role) is the one missing. Codex's assigned role is code/numerics/claims, so **the physics
audit is the gap**, which is the more consequential of the two for Phase 1–2 material.

### What the operator needs to do
Run this in a terminal with a browser available and complete the login:

```bash
agy   # then follow the OAuth URL, or:
agy --help   # check for a login/auth subcommand in this build
```

Then tell me, and I will **re-issue every degraded audit to `agy`** and reconcile its findings
against Codex's — the audit backlog is tracked below so nothing is lost.

### Degraded-audit backlog (to re-issue once `agy` is authenticated)

| Audit | Phase | Codex | agy | Re-issue needed |
|---|---|---|---|---|
| AUDIT-1 | 1 — problem definition | ✅ dispatched | ❌ auth failed | **YES** |

*(This table is appended to as further audits run in degraded mode.)*

### Alternative if re-authentication is not convenient
I can substitute a physics-focused audit by dispatching a second, differently-primed Codex instance
with agy's role brief (governing equations, force fields, closure form, Marangoni threat). This is
weaker than genuine tool diversity — a second Codex shares the first's blind spots — but it is
better than a single perspective. **I have not done this unilaterally**; say the word and I will,
or authenticate `agy` and get the real second opinion.
