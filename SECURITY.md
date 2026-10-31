# Security policy

## Supported state

There are no supported firmware or panel runtime releases yet. Current source tooling
and repository infrastructure are the reporting scope; published experiments must list
exact Android/kernel revisions, patch coverage and known limitations. A version label
or Android security patch date alone does not prove kernel, vendor or blob coverage.
No current LTS support period is declared. See [support policy](docs/releases/SUPPORT.md).

## Report privately

Use [Report a vulnerability](https://github.com/TOVSWORLD/ValethonOS-Android/security/advisories/new).
Do not open a public exploit report or include secrets in an issue. Include affected
commit/tag, device and component, reproducible steps, expected/actual behavior, impact,
and a small sanitized demonstration. Do not attack another person's tablet, processor,
network or credentials. Do not attach licensed firmware or private keys.

The owner coordinates investigation and disclosure. We aim to acknowledge reports
within seven days, with no staffed response SLA. Agree a disclosure plan case by case;
do not promise that an unavailable proprietary component can be fixed. GitHub's
security controls are the contact mechanism; there is no invented project email.

## Development boundaries

CI gets read-only tokens and no device/lab access. Signing keys and processor credentials
must stay outside Git and untrusted pull requests. Keep APK inspection static unless
an isolated runtime test has been explicitly authorized. Account for network exposure,
SELinux enforcement, update signing and rollback before claiming a supported build.
A safety-relevant regression can hold or withdraw a release regardless of its number.
