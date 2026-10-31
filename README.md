# ValethonOS for Android

Two projects share one source and evidence repository. Their linked GitHub Projects are
[ValethonOS for Android](https://github.com/users/TOVSWORLD/projects/4) and
[Crestron Panel](https://github.com/users/TOVSWORLD/projects/5).

Project source and scope:

- **[ValethonOS for Android](projects/firetabs-android/)** — maintained, general-purpose Android
  loads with a current maintained kernel appropriate to each Android release.
- **[Crestron Panel](projects/crestron-panel/)** — optional single-application panel modes,
  supported Crestron Android clients and separate native panel compatibility research.

## Current delivery

OS brand: **ValethonOS**. This repository and the Android board are
**ValethonOS for Android**, formerly FireTabs Android. Initial hardware is the
Amazon Fire HD8(2017), douglas/KFDOWI. Existing engineering paths and scope labels
retain their stable identifiers so source locks and reproducible commands keep working.

The approved software route has reached TWRP and an interim LineageOS18.1 Android11
home screen with authorized ADB. This is a working upstream lab baseline, not the
finished ValethonOS public release. Its actual security patch is2024-02-05,
encryption reports unsupported and SELinux is Permissive; these remain limitations.
Maintained-kernel source builds exist, but actual maintained-kernel boot/hardware and
independent failed-load return/retained-log gates are still unqualified.

The owner requires a stable, supported, updated **ValethonOS** release before
Connect, passkey or other feature QA. The integrated candidate includes own boot,
setup, wallpaper, launcher and About identity while retaining upstream attribution,
license notices and truthful Android/security-patch information. A new build date
or new branding does not establish security maintenance or stability.

Start with [phase progress and next steps](https://github.com/users/TOVSWORLD/projects/4/views/2)
for achieved milestones, current work and remaining phase exits.
Follow the [live delivery board](https://github.com/users/TOVSWORLD/projects/4),
[current work queue](docs/development/ACTIVE-WORK-QUEUE.md), and
[ordered roadmap](docs/development/ORDERED-ROADMAP.md). One Task is active at a time;
Execution order, Primary PR, Latest result, Next action and Blocker show how to follow
progress. Completed scopes stay visible. The exact upstream target/update strategy
is selected and qualified under#333 before a public release claim.

## Start here

Run the same inexpensive offline checks used by CI, without third-party Python packages:

```sh
python3 scripts/ci.py repository
python3 scripts/ci.py firetabs-android
python3 scripts/ci.py crestron-panel
python3 scripts/check_community.py
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

## Community and releases

Read [CONTRIBUTING.md](CONTRIBUTING.md) before sending a PR. See the
[documentation index](docs/README.md), [issue hierarchy](docs/project/ISSUES.md),
[release cadence and numbering](docs/releases/PROCESS.md), [support](SUPPORT.md),
[security reporting](SECURITY.md), and [licensing status](LICENSING.md).
