# Decision records

## Accepted — project scope (2026-10-24)

User direction: maintained general-purpose FireTabs Android plus a separate optional
Crestron panel load. Home is one workload. A panel selects one application/use mode at
a time. Native runtime compatibility is additional research, not proven equivalence.

## Accepted — kernel direction (2026-10-24)

Move to a maintained Android kernel appropriate to each target release. Android 17 is
the initial target under investigation. Legacy kernels are hardware references, not the
chosen long-term maintenance base. Exact ACK branch and driver integration are undecided.

## Accepted — branch policy (2026-10-24)

User required main locked except development-to-main releases. Development is default;
features enter through protected PRs; main requires same-repository development and CI.
Release PRs preserve history with merge commits. No direct or force pushes.

## Process baseline — releases and public contribution (2026-10-24)

Configured in response to the user's request: independent project SemVer streams,
separate source-workspace tags, monthly conditional release window, public contribution
and issue process. Product stability and LTS are evidence/support commitments, not
version-number assumptions. License selection requires an explicit owner decision.

For a new decision, add context, cited evidence, alternatives, accepted choice, status,
owner and consequences. Do not mark a proposal accepted because it appears in AI output.
