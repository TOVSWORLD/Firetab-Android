# Crestron Panel

An optional load on the maintained FireTabs Android platform. Setup selects one panel
use, then runs that application full-screen. This project does not narrow the Android
project to a Crestron-only tablet.

## Two implementation levels

1. Supported Android clients: Crestron Home (`com.crestron.phoenix.app`), and separately
   evaluated Go, ONE, and browser/CH5 clients. Build a mode selector, boot recovery,
   foreground behavior, provisioning and an administrator exit once platform APIs are
   selected. No selector application has been implemented.
2. Native panel compatibility: investigate TSW application/runtime services. Public
   APK inspection found missing JNI libraries and localhost service dependencies;
   copying a panel APK is not a demonstrated port. Hardware identity, licensing and
   platform-signature requirements remain questions, not established blockers.

## Working materials

- [Research, source citations and compatibility stages](../../docs/CRESTRON-PANEL.md)
- [Pinned downloads and static evidence](../../evidence/crestron/)
- [Static inspection tool](../../scripts/inspect_crestron_apps.py)
- [Offline project checks](../../scripts/ci.py): `python3 scripts/ci.py crestron-panel`
- [Validation state](validation.json)

No native APKs or firmware are redistributed here. The inspection tool's explicit
`--download` option retrieves approximately 79 MiB of pinned archives. Hash identity
is not signature verification. Offline CI checks recorded evidence, not runtime behavior.

## Acceptance direction

Use the lab CP4 family processor (exact variant/firmware must accompany test logs).
Evaluate control and feedback, reconnect/reboot, video/cameras, intercom/audio and
long-duration operation individually. Preserve package/version/ABI and processor details.
A successful screen launch or lighting command does not establish full functionality.
Native compatibility requires a separate proof of a real project and bidirectional
join feedback through its required services. No physical tablet operations are automated.
