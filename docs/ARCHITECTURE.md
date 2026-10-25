# Architecture and project boundaries

## FireTabs Android

The platform owns boot images, maintained kernel support, board descriptions/drivers,
Android hardware interfaces, SELinux, userspace ABI, updates and general-purpose app
compatibility. Start with douglas/KFDOWI and reuse shared MT8163 support where evidence
permits. A CPU architecture capable of a newer kernel does not supply its missing board
drivers, graphics contracts or Android interfaces automatically.

Legacy 3.18/4.9 trees and Android 10/11 work are hardware references. The chosen direction
is a maintained release-appropriate kernel with Android 17 as the initial target under
investigation. No specific ACK branch has been selected. This device has no demonstrated
Treble/GSI path; do not substitute a generic image for board integration work.

## Crestron Panel

The optional load depends on a validated Android platform. It owns provisioning and a
single selected foreground application/use mode, with a maintainer escape path and
reboot/reconnect behavior. A selector has not been written. The supported Home mobile
client and native Home touch-screen package are distinct applications.

Supported Android clients/web deployments and native panel-runtime compatibility are
separate deliverables. Native APK inspection identified external JNI/localhost services
and ARM32 libraries; service availability, runtime integration and full behavior need
proof. No identity spoof, disabled authentication or certification claim substitutes
for an actual working and authorized integration.

## Shared repository

`projects/` owns scopes, validation and version proposals. `evidence/` is the canonical
research record. `scripts/` provides offline checks and explicit source inspection.
`manifests/`, `patches/` and Dockerfile preserve reference work. Large checkout, build
and binary inputs stay in ignored `sources/`, `work/` and `out/` directories.
`releases/` owns release policy and individually reviewed release manifests.

CI validates evidence consistency and process; it does not manufacture hardware evidence.
A future build runner must be isolated from owner test hardware and processor secrets.
No default script is permitted to discover and mutate a connected tablet.
