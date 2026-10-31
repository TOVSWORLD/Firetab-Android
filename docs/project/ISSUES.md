# Issue hierarchy and triage

Use GitHub native parent/sub-issue relationships, not only lists of linked text.
The repository has exactly two project parents: ValethonOS for Android and Crestron Panel.
A parent issue tracks scope; it is not proof that the scope has been implemented.

## Three levels

1. Project parent (`level:project`): one per project; links scope and current evidence.
2. Feature or investigation (`level:feature`): a concrete outcome under one project.
3. Task (`level:task`): small reviewable work under a feature with acceptance and evidence.

Bugs, questions and test reports can begin without a parent. Triage attaches actionable
work to the relevant feature; do not invent epics just to file a question. Shared CI/docs
work has `area:repository` and one primary project parent, with cross-links when relevant.
A PR links its task using `Closes #N` for completed acceptance or `Refs #N` for partial work.
Do not close an entire feature through a partial task PR.

## Labels and state

Choose one project label for project work, one hierarchy level for scoped implementation,
one type and one lifecycle status. Canonical labels and descriptions are versioned in
`projects/github-taxonomy.json`; native GitHub issue types are not required for personal
repositories. `status:proposed` means not yet accepted implementation scope;
`status:ready`, `status:in-progress`, `status:blocked` and `status:needs-validation` are
maintainer-applied work states. Close completed work using GitHub issue state; do not
leave a competing “done” label. `priority:p0` is active security/data-loss/release danger,
`priority:p1` blocks the current outcome, `priority:p2` is normal, `priority:p3` is optional.
Maintainers set priority after triage; there is no public response SLA.

## Acceptance and completion

Every feature/task needs a problem, bounded outcome, non-goals, evidence, validation,
resource/device impact and dependencies. Cite source files and commits for blockers;
label hypotheses. Check a criterion only after examining the output. A failed experiment
can close an investigation when it answers the agreed question, with failure evidence;
it cannot close a “working driver” implementation requirement.

Milestones group a release or bounded evidence milestone. They are not hierarchy parents.
Product milestones have no date until the environment and work are credible. The monthly
cadence is a review window, not a promised firmware delivery date. Newly seeded work is
explicitly proposed; it does not authorize downloads, device actions or architecture choices.

Official mechanics: [GitHub sub-issues](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues).

## Reconcile repository metadata

`python3 scripts/setup_github.py` reports the bounded setup without network changes.
A maintainer can explicitly apply it with `--apply` using an authenticated GitHub CLI.
It reconciles the canonical labels, creates missing milestones/issues using stable seed
markers, and adds native parent links. Existing issue bodies, states and triage labels
are preserved. Review `projects/github-setup.json` after a run. This is a setup tool,
not a scheduled issue generator or evidence of approved implementation.

## Live project parents

- [ValethonOS for Android #2](https://github.com/TOVSWORLD/ValethonOS-Android/issues/2)
- [Crestron Panel #3](https://github.com/TOVSWORLD/ValethonOS-Android/issues/3)

See `projects/github-setup.json` for feature/task and milestone identities.

## GitHub Projects

The repository's Projects tab links two actual GitHub Projects, in addition to the
source folders and parent/sub-issue hierarchy:

- [ValethonOS for Android](https://github.com/users/TOVSWORLD/projects/4)
- [Crestron Panel](https://github.com/users/TOVSWORLD/projects/5)

Each contains its project/feature/task issues; shared repository issues appear in both.
Status uses Todo, In Progress and Done, with closed completed tasks marked Done.
Board visibility is managed separately from repository visibility; it is private until
the owner explicitly approves publication. The setup tool preserves board identities
but does not synchronize membership/status automatically. Maintainers add new issues
to their applicable board and update status when work changes.
