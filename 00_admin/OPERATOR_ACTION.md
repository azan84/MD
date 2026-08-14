# OPERATOR ACTION REQUIRED

*(Currently: none open.)*

---

## OA-1 — ~~`agy` authentication expired~~ **WITHDRAWN — my diagnosis was wrong**

**Raised 2026-08-14 during Audit 1. Withdrawn the same day. No operator action needed.**

### What I claimed
That `agy` required an interactive Google OAuth login this environment could not provide, making it
a standing-order S3.2 credential blocker, and that all audits would run single-auditor until the
operator logged in.

### What was actually wrong
The operator corrected me. On re-testing, the underlying error was **not** authentication:

```
Error: Eligibility check failed: failed to get profile picture:
Get "https://lh3.googleusercontent.com/a/...": dial tcp [2404:6800:4001:816::2001]:443:
connect: network is unreachable
```

Diagnosis:
- `agy` **is authenticated** — it has a profile; it was fetching that profile's picture.
- `lh3.googleusercontent.com` resolves to **both A and AAAA** records.
- This WSL2 instance has **only a link-local IPv6 route** (`fe80::/64`) and no global IPv6 route.
  Verified: `curl -4` to that host returns HTTP 400 (reachable); `curl -6` returns 000 (unreachable).
- When the eligibility check picked the AAAA record it failed, and `agy` **fell back to prompting
  for re-authentication**. I read the fallback prompt as the cause rather than the symptom.

The condition is **intermittent** — the DNS/route path succeeds much of the time, which is why `agy`
worked earlier in the same session. On retest it succeeded on three consecutive attempts.

### Resolution
`agy` is fully functional. **Audit 1 has been re-issued to `agy`** and the audit is no longer
single-auditor.

### The lesson, recorded so it does not recur
**Retry transient network failures before declaring a blocker, and read the whole error rather than
the last line.** The re-auth prompt was the most visible part of the output and I anchored on it;
the actual cause was two lines above, in the eligibility check. Writing an `OPERATOR_ACTION.md`
that asks a human to fix a non-problem is worse than useless — it spends the operator's attention,
which is the scarcest resource in an autonomous run.

**Standing rule adopted:** before any S3 hard-stop declaration involving an external service —
retry at least twice, capture the *full* stderr, and distinguish transport failure from credential
failure. A `network is unreachable` or DNS timeout is **never** an S3.2 credential stop.

### Residual note (informational, not action)
If `agy` fails this way again, it is IPv6-related, not credentials. A permanent fix would be to
prefer IPv4 in `/etc/gai.conf` or disable IPv6 in WSL — both need root, which this session does not
have. Retrying is sufficient and is what the run now does.
