# Security policy

OSJ is an educational edition. Only the latest OSJ source is reviewed for fixes;
there are no production-support or response-time guarantees.

Use GitHub's **Security → Report a vulnerability** on this repository if enabled.
If the private reporting option is unavailable, open an issue asking for a private
security contact **without technical details**, and wait for a maintainer to
establish a private channel. Do not submit exploits, credentials, client documents,
raw chats or personal information in public issues.

Reports should describe affected behavior, a minimal synthetic reproduction and
impact. Maintainers should triage, reproduce, fix and validate before publishing
an advisory with remediation when appropriate. Removing a report is not a fix.
Do not probe infrastructure you do not own or have permission to test.

## Maintainer publication checklist

Run publication checks and pinned Gitleaks on the candidate tree and its reachable
history. Enable GitHub secret scanning/push protection and private vulnerability
reporting where available. Repository settings are external to this source tree;
the presence of this policy does not claim these settings have been enabled.
Keep cloud trust and production credentials outside this learning repository.
If a real secret is exposed, revoke or rotate it before assessing Git-history cleanup.
