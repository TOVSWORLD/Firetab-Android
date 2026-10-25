# Project direction: maintainable Android ports for legacy Fire tablets

User direction, 24 October 2026: make legacy Fire devices useful as general-purpose
Android tablets through a repeatable pathway for maintaining supported Android releases.
Crestron Home is one required application, alongside broader everyday tablet use.
A dedicated control panel or a one-off older Android port does not satisfy the objective.

## Agreed kernel and platform direction

Port a current, maintained Android kernel appropriate to the target Android release to
the hardware, and keep kernel support moving with future Android releases. Android 17
is the initial platform target under investigation. Select the exact Android Common
Kernel branch and support lifetime through source-based compatibility research; no
specific kernel version has yet been selected or validated for douglas.

The existing 3.18 and 4.9 douglas trees provide hardware descriptions, drivers, boot
contracts and regression references. Keeping those old kernel bases alive through an
expanding set of backports is not the selected long-term strategy. Intermediate Android
builds may be used for a specific diagnostic purpose if justified later; they are not
mandatory release milestones or the destination.

The work is to identify existing support in the current kernel, forward-port or replace
missing drivers, adapt Android hardware interfaces, and validate the resulting device.
Inventory panel, touchscreen variants, PMIC/regulators, storage, USB, battery/thermal,
Wi-Fi, Bluetooth, sensors, audio, cameras and graphics. Preserve or replace proprietary
userspace/kernel contracts deliberately. Reuse common MT8163 work and upstream changes
where practical to reduce the cost of subsequent Android/kernel upgrades.

## General-purpose functionality

Target ordinary tablet functionality: installation and updates of compatible apps,
supported browsers and WebView, networking, display/touch, audio/video playback,
storage/SD card access, USB, sensors, charging, power management and suspend/resume.
Google Play/services remain a requested capability where feasible. Include broader app
compatibility, multitasking and sustained everyday use in performance testing, alongside
full Crestron Home functionality.

Features for hardware the device does not possess may be unavailable, as on other Android
devices. Declare capabilities accurately so apps can detect them. Distinguish physically
absent hardware from present hardware whose driver has not yet been ported; record the
latter as an implementation gap. Document limitations and their effect on apps rather
than treating every missing optional feature as a platform-wide blocker. CPU, RAM and
storage constraints require measurements, not an assumed Android version ceiling.

## Required maintenance deliverables

### Separate Crestron panel-mode research track

**Research update:** [CRESTRON-PANEL.md](CRESTRON-PANEL.md) records the completed
initial source and binary investigation. Three public panel APKs were statically
inspected. The HTML5 and Home panel paths require a missing Crestron JNI/service
layer; all three inspected APKs bundle ARM32 native libraries. Keep supported
Android clients and a native-runtime compatibility experiment as separate paths
on the same current-Android/current-kernel platform. Obtain and inventory the
missing panel services before promising native equivalence. No APK was executed.

The general-purpose Android port remains the foundation. The user also wants a
distinct optional panel role matching a native Crestron touch screen: select an
application/use mode in setup, then run one selected application full-screen at a
time. This is not a request for simultaneous applications or an ordinary app switcher.
Running the Crestron Home Android app satisfies the Home application requirement;
native panel-mode compatibility is additional research, not a prerequisite for it.

Verified references as of 24 October 2026:

- [TSW-70 application selection](https://docs.crestron.com/en-us/8550/Content/Topics/Configuration/Application-Setup.htm)
  documents a single selected app, Crestron-approved delivery and multiple modes,
  including Home and scheduling/partner applications. The
  [installation guide](https://docs.crestron.com/en-us/8550/Content/Topics/Installation/Installation-TSW-70.htm)
  also describes User Project selection and uploads through the web interface or Toolbox.
- [Crestron Go for Android](https://www.crestron.com/Products/Catalog/Control-and-Management/Software/Programming-Commissioning/CRESTRON-GO-ANDROID)
  provides an Android client for Smart Graphics projects and 3-Series, 4-Series and
  VC-4 systems. This is a mobile-client route, not proof of native TSW firmware compatibility.
- [Crestron ONE Android configuration](https://docs.crestron.com/en-us/9580/Content/Topics/Configuration/Configuration.htm)
  documents HTML5/Construct project loading and Android 14+ prerequisites.
- [HTML5 User Interface](https://www.crestron.com/Products/Catalog/Control-and-Management/Software/Programming-Commissioning/Crestron-HTML5-User-Interface)
  also supports compatible Android browsers through Web XPanel. Browser, mobile
  and native-panel deployments require separate compatibility/feature verification.

Two implementation levels must remain explicit:

1. An Android-based panel mode selector using supported Android clients and web
   runtimes, with kiosk/boot behavior, configuration and app lifecycle management.
   This is technically plausible, subject to each app's compatibility and capabilities.
2. Porting native Crestron panel runtimes/services so the tablet accepts native panel
   projects and supports equivalent configuration, processor integration and management.
   Feasibility is unverified. A selector UI or a changed device identity does not
   establish those behaviors. “Any Crestron application” is not a validated scope.

For the second level, inventory firmware packages and native/Java services, identify
framework/HAL dependencies, project runtimes and deployment protocols, and determine
whether usable source/SDKs or appropriately available binaries exist. Hardware binding,
provisioning, certificates, entitlement checks and redistribution constraints are
questions to investigate, not blockers demonstrated by this research. Verify current
licensing per selected runtime. The current licensing portal confirms the old
ONE/HTML5 mobility license is no longer required with current software; older
SW-MOBILITY documents must not be used as a blanket blocker.

Classify every desired mode as supported Android client, supported web deployment,
native runtime candidate, or unresolved. Evaluate custom Smart Graphics and HTML5
projects, Home, scheduling and relevant partner apps independently. Native panel
equivalence needs evidence for the applicable Toolbox upload/configuration workflows,
processor registration, device management, audio/intercom, video and lifecycle behavior.
No native firmware extraction, runtime port or panel-mode prototype has been performed.

### Shared platform maintenance

- A common MT8163 hardware layer with per-board configuration, not copied complete
  trees for each release. Giza, douglas and Echo device differences remain explicit.
- A feature audit citing required Android source/API and matching kernel
  implementation, resolved config, test and result. Unknown is a valid status.
- Versioned blob inventories with hashes, ABI/symbol requirements and source
  provenance. Isolate graphics/audio/camera compatibility adapters instead of
  broadly weakening libc or Android security checks.
- Locked complete platform manifests and compiler/container digests, separate
  kernel/platform patch queues, repeatable image-content/size checks and CI.
- A physical test matrix: boot, display/touch, networking and UID filtering,
  suspend/resume, audio/video, relevant cameras, general-purpose app/browser/media tests, Home full-function tests, Google
  service installation, enforcing SELinux and long-duration operation.
- A release policy defining supported Android branches, security-update cadence,
  kernel/blob coverage, signing keys, reproducible build records, upgrade/rollback
  procedures and the criteria for ending a branch. Define “LTS” as a concrete
  project support commitment, separately from Linux LTS or upstream patch availability.

## Next engineering milestone

Produce a **current-kernel hardware-support and Android 17 integration audit** for
douglas. Choose a candidate maintained kernel branch, map existing and missing board
support, identify reusable driver implementations and proprietary interface constraints,
and define staged bring-up tests. Use the older kernels as references. Include
executable capability tests where practical; symbols or defconfig entries alone do not
establish functionality.

The user will provide the next instructions. This document update does not begin a
kernel port, large download, build, or physical device operation.

Current work is source inspection and initial Android 11 patch adaptation only.
No feature-gap audit, maintained kernel, complete build environment, Android 15/17
port or device validation is claimed complete. Repository CI is now implemented; it
validates evidence consistency and does not build or run firmware. See CI.md.
