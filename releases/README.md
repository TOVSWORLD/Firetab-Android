# Release manifests

`policy.json` is the versioned release convention. `manifests/` contains reviewed release
candidates/records; no manifest or tag is created merely because a monthly window arrives.
There are currently no product or workspace release manifests.

A manifest is a JSON object with:

- `project`: workspace, firetabs-android or crestron-panel.
- `version`: MAJOR.MINOR.PATCH with optional alpha.N, beta.N or rc.N.
- `tag`: policy prefix plus version.
- `kind`: source-snapshot, firmware or panel-load as allowed by project.
- `tested_revision`: exact 40-character commit SHA.
- `notes`: existing nonempty repository Markdown path, with truthful limitations.
- `native_runtime`: boolean; only panel-load may claim true.
- `artifacts`: list of objects containing local-relative `path`, positive `bytes`, `sha256`.
  Empty for source snapshots; mandatory for runtime loads. Do not commit restricted binaries.
- `provenance`: required runtime fields `source_manifest`, `toolchain`, `device_matrix`,
  each naming an existing nonempty repository text record; source_manifest must include
  complete pinned source and toolchain references, not just the old inspection lock.
- `support_record`: repository path required for rc/stable runtime releases; includes
  project, version, maintainer, starts, ends and tested procedure paths. See SUPPORT.md.

Use `python3 scripts/check_release.py releases/manifests/NAME.json` for metadata checks.
For local artifact content verification before publication append `--artifact-root /PATH`;
each named file must then match size/hash and stay inside that directory. This command
never creates tags, uploads artifacts or contacts the network. Tests construct temporary
fixtures; those fixtures are not release evidence.
