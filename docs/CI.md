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

Three named GitHub validation jobs run on every PR and development/main push: Repository integrity, FireTabs
Android evidence, Crestron Panel evidence. The repository job also runs adversarial
unit tests for the gate logic. Actions are commit-pinned; permissions are read-only,
credentials are not persisted, timeouts are bounded and obsolete runs are cancelled.
PR code receives no secrets. A separate `pull_request_target` workflow checks only
GitHub event metadata; it never checks out or executes PR content and has read-only
permissions. Its required `Release source policy` check rejects main PRs unless their
source is this repository’s `development` branch.

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

Default CI performs no kernel/platform checkout restore, AOSP sync, APK download,
firmware build or flash. The Android job explicitly fetches the small pinned dtc/Meson/
Ninja tool inputs to compile the tracked DT-only experiment.
Large builds and device tests require a later concrete workflow and provisioned host.
Never run untrusted PR code on a lab runner with USB devices or processor credentials.
When builds become possible, add independent artifact checks (architecture, partitions,
hashes, build logs) and test stages before release automation. Do not add a successful
empty build job now. Required-status branch protection must be enabled separately once
the named checks exist; workflow files alone cannot enforce GitHub merge settings.


## Branch and release policy

`development` is the default integration branch. Feature and fix PRs target it and
must pass the three validation checks. `main` accepts releases only through a PR from
this repository's `development` branch, with all three checks and the metadata-only
release source check required. Protection applies to administrators too; direct pushes,
force pushes, and branch deletion are disabled. No automatic merge or publication.

Use merge commits for development-to-main releases so development remains an ancestor
of main; do not squash or rebase the release PR. GitHub's literal branch-lock setting
is not used because it would also block the intended release merges.

## Community and release checks

Repository integrity also runs `scripts/check_community.py`: required public docs,
tracked local Markdown link targets, seven JSON-syntax YAML issue forms and their label
references, release policy and all committed release manifests. The release checker
rejects runtime candidates without applicable evidence at the exact tested revision.
Stable/rc candidates also need active named support and install/upgrade/recovery records.
Local artifact size/content verification is explicit and must precede publication.
External links, legal rights, log truth and artifact signatures still need human review.

Actions dependency updates are proposed monthly against development through Dependabot;
its PRs use the same checks and do not merge automatically. Release-note categories
can group reviewed PRs by project, but maintainers still supply validation and limitations.

Repository integrity now also runs `scripts/kernel_audit.py` offline to verify the pinned
modern-kernel source snapshot and component claim anchors. It does not run the optional
clang dependency-failure probe, build a kernel or establish device support.

## Actual device-tree compilation

FireTabs Android evidence now builds pinned dtc/fdtget in work/ and runs the real
`build_douglas_dtb.py` compile/inspection on Linux. It rejects warnings, errors and
unreviewed DTB content changes. Repository integrity also verifies input/patch hashes.
This establishes DT syntax/binary reproducibility only. Full binding validation is
not passed; the incomplete-context local schema attempt is separately recorded.
No kernel_compile, boot or hardware stage is promoted by this job.

The heavy `kernel-baseline.yml` experiment runs on PR open/ready-for-review and
manual dispatch. Documentation updates do not restart a whole kernel compile.
After a source/config/tool/build-script change, explicitly dispatch it on the
feature branch and record the exact run/revision before accepting compilation.
A source-identical older run may support a documentation update; explain that
comparison. Ordinary required repository checks still run on every PR update.
The textual clock-reference audit is reproducible with
`python3 scripts/audit_clock_references.py --check`; it records unresolved parents
and never represents a schema or hardware validation pass.
