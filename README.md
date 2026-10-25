# Firetab Android

Two projects share one source and evidence repository:

- **[FireTabs Android](projects/firetabs-android/)** — maintained, general-purpose Android
  loads with a current maintained kernel appropriate to each Android release.
- **[Crestron Panel](projects/crestron-panel/)** — optional single-application panel modes,
  supported Crestron Android clients and separate native panel compatibility research.

Initial hardware: Amazon Fire HD 8 (2017), douglas/KFDOWI, 16 GB, Fire OS 5.7.1.0.
Initial platform target: Android 17. Status: research, static inspection and historical
patch preparation only. No firmware has been compiled, booted, flashed or validated.

## Start here

Run the same inexpensive offline checks used by CI, without third-party Python packages:

```sh
python3 scripts/ci.py repository
python3 scripts/ci.py firetabs-android
python3 scripts/ci.py crestron-panel
python3 -m unittest discover -s tests -v
```

[Continuation and resources](docs/CONTINUE.md) describes source restoration and build-host
requirements. Full Android builds need a separate Linux x86_64 environment with a
case-sensitive filesystem and at least 400 GiB available; 64 GiB RAM is preferred.
The root Dockerfile is an unbuilt historical Android 11 recipe, not an Android 17 SDK.
Source checkouts, APKs and build outputs are ignored, not bundled with this repository.

[CI and AI development policy](docs/CI.md) explains evidence levels, change review and
what a green check establishes. [Work log](docs/WORKLOG.md) records actual work.
[Maintenance strategy](docs/MAINTENANCE.md) records the user-selected kernel direction.

Research references retain their original authorship and licensing. No blanket license
is asserted over third-party evidence or proprietary materials; check upstream terms
before redistribution. This repository does not contain an authorized Google services
bundle or Crestron firmware distribution.

Development targets `development`; `main` accepts development-to-main release PRs only.
See [branch and release policy](docs/CI.md#branch-and-release-policy).
