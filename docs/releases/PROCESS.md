# Release numbering, cadence and process

## Version streams

Use [SemVer 2.0.0](https://semver.org/) independently for two products:

- `firetabs-android-vMAJOR.MINOR.PATCH[-alpha.N|-beta.N|-rc.N]`
- `crestron-panel-vMAJOR.MINOR.PATCH[-alpha.N|-beta.N|-rc.N]`

Repository/tooling/source snapshots use `workspace-vMAJOR.MINOR.PATCH` with the same
optional prerelease syntax. A workspace tag is never an installable firmware claim.
Initial proposed versions are workspace 0.1.0 and product 0.1.0-alpha.1; none is published.
Android 17/API 37, LineageOS 24, kernel versions and app versions remain separate fields
in release metadata. Project version 17 is not implied by target Android 17.

The public compatibility contract is supported device/partition layout, install/upgrade
and recovery behavior, configuration/data schema and panel-facing provisioning APIs.
Major increments change that contract incompatibly; minor increments add compatible
capabilities; patch increments fix compatible behavior. Before 1.0, incompatible contract
changes increment MINOR and need migration notes. Alpha is experimental bring-up; beta
means feature-complete for the stated scope with outstanding validation; rc means the
stable gates are satisfied and the candidate is being confirmed. A prerelease suffix
never excuses inaccurate feature or security claims. Published tags are immutable:
correct a release with a new version, never retarget or reuse a tag. An active tag
ruleset blocks update and deletion of the three release tag prefixes without bypass.

## Cadence (America/New_York)

Maintain a monthly release **window on the first Tuesday** of each month. Scope cutoff
is the preceding Tuesday; prepare an eligible RC by the preceding Thursday. Publish only
if gates pass. The first review window after setup is 2026-11-03, not a promised image.
Release a source workspace snapshot only when meaningful reviewed changes exist.
Product streams may skip any window while bring-up/testing is incomplete. Urgent
security or severe regression fixes use an out-of-cycle patch after the same gates.
No timer auto-merges, creates tags, publishes assets or changes devices.

## Gates by release kind

- `source-snapshot`: workspace project only, notes explicitly say no runtime artifact;
  source/evidence checks pass, changelog and notices are reviewed.
- `firmware`: Android project only. Alpha/beta requires genuine kernel/Android compile
  and boot evidence at the exact tested revision. Every hardware gap is listed. Stable
  and rc additionally require hardware and general-purpose soak stages to pass, an
  active support record and documented install/upgrade/recovery for the device.
- `panel-load`: panel project only. Alpha/beta requires real client-runtime and CP4
  integration evidence on a named platform. Stable/rc also requires full-function soak,
  active support record and documented provisioning/upgrade/recovery. A native runtime
  claim additionally requires its own passing native-runtime stage.

All runtime artifacts need exact SHA256/size records and source/toolchain provenance.
Test records refer to the candidate's exact source revision, not automatically to the
later release merge commit. The release merge must contain that tested revision and
must not change relevant code after testing. Review this explicitly; an ancestor check
alone cannot prove equivalence. Google and Crestron redistribution rights are separate
acceptance gates. Do not publish restricted binaries under an umbrella project license.

## Maintainer procedure

1. Pick one project/version and open a release issue with scope, channel, blockers,
   evidence, compatibility/migrations and rollback. Keep two product versions independent.
2. Complete normal feature/fix PRs into development. Record tested revision and source,
   compiler/container pins, artifacts and test logs. Update CHANGELOG.md and limitations.
3. Create a release manifest under `releases/manifests/` using the documented schema;
   validate it with `python3 scripts/check_release.py PATH`. Repository CI checks every
   committed manifest. No runtime manifest is valid from today's untested project state.
4. Open **development → main** release PR. Confirm all required checks pass and review
   the actual outputs and exact revision. Use a merge commit, retain development, and
   do not use `--admin`. A feature PR cannot release directly to main.
5. Fetch main and identify the release merge SHA. Confirm the tested revision is an
   ancestor (`git merge-base --is-ancestor TESTED_SHA origin/main`) and the manifest,
   notes and relevant source are the reviewed versions. Run checks again and verify each
   runtime file locally using the checker's explicit `--artifact-root` option.
6. Create an annotated, preferably signed, tag with the exact configured prefix pointing
   to that main merge SHA. Draft the GitHub release using the release-note template.
   Attach only permitted artifacts, SHA256SUMS, component notices/source offer where
   required, source manifest and build/test records. Mark alpha/beta/rc as pre-release.
7. Independently inspect draft notes, artifact architecture/partition sizes/signatures
   and download hashes. The owner explicitly publishes after review. No release workflow
   here automatically uploads or publishes anything.
8. Record the tag/release link in the issue, close the milestone only if its scope is
   complete, and update CHANGELOG on development for the next cycle. Keep release evidence.

Examples of tag/draft commands, **only after the steps above**:

```sh
git tag -a workspace-v0.1.0 MAIN_RELEASE_SHA -m 'Source workspace 0.1.0; no firmware'
git push origin workspace-v0.1.0
gh release create workspace-v0.1.0 --verify-tag --draft --notes-file RELEASE_NOTES.md
```

Current automation validates metadata, not artifact authenticity, license compliance or
hardware truth. Tag creation/publication remains maintainer-controlled; branch CI alone
does not prevent a write-authorized user from creating a tag on an unrelated commit.
See [GitHub release mechanics](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
