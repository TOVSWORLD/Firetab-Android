# Troubleshooting

## Repository check fails

Read the first concrete exception. Run the same command from repository root. Check
JSON/XML syntax, pinned revisions and evidence hashes rather than editing expected
values blindly. New files must be staged to enter the tracked-file check. A large
intentional deletion needs its exact previous-content hash and a review reason in
projects/change-exceptions.json; this is not permission to hide accidental truncation.

## Source checker or restore fails

Normal CI does not need source clones. `check_sources.py` needs restored locked checkouts
and the historical vendor-path patch described in CONTINUE.md. Restore refuses a wrong
existing revision rather than resetting your work. Inspect that checkout's git status;
preserve modifications before choosing a different directory. A dirty kernel checkout
on a case-insensitive filesystem may be a filename collision; use a case-sensitive host.

## Preflight exits nonzero

The macOS inspection host is expected to fail full-build preflight. Read the recorded
OS, architecture, disk and filesystem checks. Do not weaken thresholds to make an
unsuitable host appear ready. Provision the intended Linux environment separately.

## APK inspection fails

Check SDK apkanalyzer/Java availability and pinned input archives. A missing archive
does not auto-download. A public URL may disappear; keep the failure record and locate
an authorized replacement with new provenance instead of silently changing a hash.
A missing native library is dependency evidence, not proof of an unavoidable blocker.

## PR cannot merge

Features target development. Main accepts only same-repository development release PRs.
All required checks must finish on the current candidate; updating a branch reruns them.
Do not bypass protection with an admin push. A release uses a merge commit and retains
development. Open a focused issue for a broken check with the actual run link/output.
