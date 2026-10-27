# Delivery workflow

Work uses **Epic → Feature → Phase → Task**. Native GitHub parent links are the
source of hierarchy; the Level field and level labels mirror that relationship.
An epic is a product outcome, a feature is a deliverable, a phase is a gated stage,
and a task is a reviewable unit with concrete acceptance. Do not create an issue
for every heartbeat, comment, evidence receipt or routine check. Update the active
task until its acceptance is met; split only for independently reviewable work.

The Android and Crestron boards have Level and Delivery state fields. Ready means
independent work can start; Blocked names missing evidence/dependencies; Active
means work is actually executing; Ready for QA requires beta admission evidence;
Done requires the issue's acceptance. GitHub's closed state for an audit means only
that audit completed. It never passes a parent's hardware/runtime gate. Completed
historical evidence can be archived on the board without deleting its issue.

Every PR needs a standalone `Updates #123` (or `Refs #123`) for partial progress,
or `Closes #123` / `Fixes #123` / `Resolves #123` when all issue acceptance is met.
Use the task issue where possible, and update its result, remaining work and parent
phase. The PR issue linkage check validates real same-repository issues, rejecting
missing references, template comments, code examples and PR-number substitutions.
It checks traceability, not whether a claimed result is true: review still must
confirm acceptance and evidence. Link-only PRs must also update the issue with the
actual result; do not close broad phases through a small supporting change.

All feature PRs target development. Main changes only through development-to-main
release PRs. The issue-link check is required alongside existing validation checks.
No CI completion, issue transition or roadmap authorizes tablet access, firmware/
helper execution, flashing, wiping, downgrading or paid/large resource use.

Beta ready for QA is an admission milestone, not a date or a claim of full support.
Mandatory evidence includes a reproducible exact candidate; qualified loading,
original-state recovery and real logs; actual douglas boot; essential display/input,
connectivity/storage/power smoke; security configuration and license/provenance
review; known-issue triage; tester steps, stop criteria and an explicit admission
review. Every required result identifies its revision and evidence. No known
critical safety, recovery or data-loss blocker may remain. Optional or unsupported
features must be named, with their tests clearly excluded rather than marked pass.
Crestron QA is a separate product gate and does not hold Android beta hostage;
native panel parity is excluded until independently demonstrated.

No calendar estimate is committed until recovery feasibility, scope and resource
estimates support one. Replan the phase dependencies when evidence changes rather
than generating more completed micro-issues. The current critical path starts with
qualified recovery and capture; source-only board/build and QA-plan work can proceed
where their task acceptance does not depend on a physical test.
