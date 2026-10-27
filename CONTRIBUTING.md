# Contributing to Firetab Android

Welcome. The purpose is to maintain useful general-purpose Android on existing Fire
hardware, with a separate optional Crestron panel load. Research, driver work, tests,
reproduction reports and documentation are all useful contributions. No working
Android 17 firmware or native Crestron panel port has been released.

## Before contributing

1. Read the [project status](docs/README.md), [architecture](docs/ARCHITECTURE.md),
   [development guide](docs/development/SETUP.md) and [licensing policy](LICENSING.md).
2. Search existing issues. Choose the appropriate project and smallest useful task.
   For a new feature or costly experiment, open a proposal before substantial work.
3. Read the [code of conduct](CODE_OF_CONDUCT.md). Send vulnerabilities through
   [private reporting](SECURITY.md), not a public issue.
4. Confirm that you have rights to contribute the material. Do not upload vendor APKs,
   firmware archives, Google packages, keys or private lab data.

Licensing is an explicit acceptance gate: follow the current policy in LICENSING.md.
A public repository alone does not license its contents.

## Get a checkout and run checks

```sh
git clone https://github.com/TOVSWORLD/Firetab-Android.git
cd Firetab-Android
git switch development
git switch -c fix/descriptive-name
python3 scripts/ci.py repository
python3 scripts/ci.py firetabs-android
python3 scripts/ci.py crestron-panel
python3 scripts/check_community.py
python3 -m unittest discover -s tests -v
```

Fork the repository if you do not have write access. Push your branch to your fork and
open a PR against **development**, never main. Main is reserved for same-repository
development-to-main releases. Use `feat/`, `fix/`, `docs/`, or `research/` branch prefixes.
Keep commits focused and explain the behavior and reason in the subject/body. No strict
commit-title parser is required. Do not rewrite shared branches.

## Evidence and implementation standards

- Link the parent issue; describe before/after behavior and acceptance criteria.
- Pin source commits and download hashes. Preserve upstream authorship, patch origin
  and licenses. Explain any deviation from upstream APIs or behavior.
- Prefer shared MT8163 support with board-specific differences. Do not duplicate whole
  device trees per Android version without explaining why sharing is impractical.
- Distinguish static inspection, compilation, boot, hardware tests and application
  reliability. Never call a generated image “working” based on compilation alone.
- Fix the root cause. Do not replace a missing service with an inert implementation,
  disable tests, relax SELinux, or hide failures to get a green check.
- Unknowns and reproducible failed experiments are valid results. Record the exact
  failure and next discriminating test; a proposal is not implemented functionality.
- New tests should exercise meaningful behavior and failure paths. Do not add assertions
  that merely repeat implementation constants or claim hardware coverage from fixtures.

Use [testing guidance](docs/development/TESTING.md) for logs and the test report form.
No physical operations are required to contribute. Only an owner with an explicit test
plan should unlock, flash, wipe or change a tablet; repository scripts and CI must not.

## AI-assisted contributions

AI tools are allowed. The submitting human remains responsible for correctness,
provenance, review and test results. Disclose material AI assistance in the PR; list
what was actually reviewed and executed. Verify source files and APIs yourself.
Do not upload secrets, proprietary firmware, personal logs or other contributors'
private material to a model service. AI-generated plans or issue text are not evidence
of approved scope or implemented features. See [CI policy](docs/CI.md).

## Review and merge

Use the PR template. Include commands and actual output, unperformed tests, resource
costs, privacy review, and the affected project's validation record. Contributors may
leave that record unchanged when their change does not establish a new validation stage.
Maintainers check licensing, behavior, source evidence, tests and release implications.
All required CI must pass; green CI alone does not require a maintainer to merge.
Maintainers squash feature PRs or preserve meaningful commits as appropriate. Releases
from development to main always use a merge commit and retain development.

A checked issue is complete only when acceptance criteria are evidenced and its code
or documentation has merged into development. Track release inclusion separately;
GitHub's default-branch closing behavior is not a production deployment indicator.
See [work hierarchy](docs/project/ISSUES.md) and [release process](docs/releases/PROCESS.md).

## Delivery and PR traceability

Follow [Epic → Feature → Phase → Task](docs/project/DELIVERY-WORKFLOW.md). Every PR
must explicitly update or close a real issue; use the task and retain open runtime
gates. See the [beta roadmap](docs/project/ROADMAP.md) for admission criteria.
