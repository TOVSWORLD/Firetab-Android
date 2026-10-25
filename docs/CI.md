# CI and AI-assisted development

## Lessons adapted from Valethon

Reviewed local Valethon AGENTS.md sections “Do NOT Treat Codex-Generated Content as
Authoritative”, “Code Completeness”, “NEVER Create Stubs”, and “Always Verify Before
Reporting”, plus its actual `.gitlab-ci.yml` truncation and canonical-writer checks
on 2026-10-24. These are provenance for the lessons, not imported project rules.
Valethon code, credentials and internal business data are not copied here.

Apply those lessons to this repository as follows:

- Research proposals are not implemented features. Verify code, source pins and actual
  logs rather than citing another AI-written plan as proof.
- Shared source pins and inspection evidence are canonical; project entry points link
  to them rather than duplicating them.
- CI validates its own rejection paths. Missing comparison commits fail instead of
  silently skipping the truncation check. Large losses/deletions require an exact
  old-content SHA256 and reason in `projects/change-exceptions.json`.
- No fake implementations to make builds green; changed first-party Python is checked
  for explicit unimplemented bodies. Review still must detect semantic omissions.
- Proposed work and truthful missing-feature documentation are allowed. Unlike a broad
  keyword ban, historical upstream evidence and descriptions of gaps remain intact.
- Keep PR checks small and blocking. No duplicate full builds, paid model calls,
  privileged runners, auto-merge, auto-release or physical device access.

## What runs

Three named GitHub jobs run on every PR and main push: Repository integrity, FireTabs
Android evidence, Crestron Panel evidence. The repository job also runs adversarial
unit tests for the gate logic. Actions are commit-pinned; permissions are read-only,
credentials are not persisted, timeouts are bounded and obsolete runs are cancelled.
PR code receives no secrets. There is no `pull_request_target` workflow.

Checks cover Python syntax, JSON/XML parsing, source-pin safety, historical manifest
revisions, APK evidence/package/hash agreement, and ordered validation records.
The change guard detects substantial text truncation and deletion. It is a heuristic;
review must assess legitimate refactors and small but harmful deletions.

These are deterministic checks informed by AI-development lessons, not an autonomous
AI review service. No model account or API key has been configured. The PR template
requires review of actual behavior, test output and AI-generated assumptions.

## Validation and promotion

Each project owns `validation.json`. States are `not_run`, `failed`, or `passed`.
Passing a stage requires a revision and nonempty hashed evidence records present in
Git. Stages must pass in order. Do not edit a status to pass without the actual test.
CI validates record structure and content identity; it cannot prove a log is truthful.
Independent review of logs and physical results remains required.

Android stages: kernel compile, Android compile, boot, hardware, general-purpose soak.
Panel stages: client runtime, CP4 integration, full-function soak, native runtime.
Native runtime is tracked separately and is not required for supported Android client
experiments; it is last because no native parity claim precedes client validation.
All are currently `not_run`. A green PR is never a firmware or panel release.

## Resource boundaries

Default CI performs no source restore, AOSP sync, APK download, firmware build or flash.
Large builds and device tests require a later concrete workflow and provisioned host.
Never run untrusted PR code on a lab runner with USB devices or processor credentials.
When builds become possible, add independent artifact checks (architecture, partitions,
hashes, build logs) and test stages before release automation. Do not add a successful
empty build job now. Required-status branch protection must be enabled separately once
the named checks exist; workflow files alone cannot enforce GitHub merge settings.
