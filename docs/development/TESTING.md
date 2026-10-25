# Testing and evidence

## Levels of evidence

1. Static analysis: source/ABI/dependency inspection and consistency checks.
2. Compilation: exact source/toolchain and genuine kernel or platform build logs.
3. Boot: owner-authorized run on identified hardware with console/kernel/Android logs.
4. Hardware: per-component results, power, suspend/resume, networking and security.
5. Workload/soak: sustained general-purpose or full selected panel functionality.

A higher level needs new evidence; green repository CI establishes only level 1.
Evidence records must identify the exact tested revision and sanitized nonempty logs
with SHA256 hashes. Keep failed attempts as failed results rather than deleting them.
The release checker requires evidence stages to refer to the candidate's exact revision.
A later code change invalidates assuming an older result still covers the candidate.

## Android acceptance

Record boot/recovery image sizes and partition fit, display/touch variants, storage/SD,
USB, wireless, audio, media/camera paths, sensors, charging/thermal, suspend/resume,
SELinux enforcing and denials, browser/WebView, app installation and update/recovery.
Identify hardware absent by design versus present but unported. A passing app launch
is not a GPU/media, network UID filtering or suspend test. Capture memory pressure,
free storage and duration under a declared workload. Stable acceptance requires a
minimum 72-hour soak with repeated suspend/reconnect cycles and no release-blocking
regression; disclose environmental limits and untested configurations.

## Panel acceptance

Identify mobile vs native package, version/ABI, Android revision, exact CP4 variant and
firmware. Test controls and feedback, authentication, reconnect, processor restart,
tablet reboot, selected-app persistence and administrator exit. Exercise every claimed
mode including cameras/video and intercom/audio; mark unsupported or untested features.
Stable app-load acceptance requires a minimum 72-hour full-workload soak on the declared
platform/processor matrix. Native runtime parity has its own test claim and evidence.
Do not imply TSW management/certification from client control behavior.

## Physical tests and privacy

Only the owner authorizes and performs device-changing tests for now. Agree the exact
image/hash, device, commands, rollback/recovery and data handling before any unlock,
flash or wipe. This guide grants no such authorization and supplies no flashing script.
Use the test-report issue form. Record commands as executed, timestamps and results.
Redact serials, MACs, credentials, private addresses and customer content before posting.

## Local and CI checks

Run the five commands in CONTRIBUTING.md. Gate unit tests must reject corrupt evidence,
missing proof and unsupported claims. `scripts/check_release.py` validates a proposed
release manifest without publishing it. Hardware and native-library behavior cannot
be replaced by synthetic fixture results. No model service or lab credentials run in CI.
