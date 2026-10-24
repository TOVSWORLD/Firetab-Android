# Crestron panel research and project direction

Assessed 24 October 2026. Scope: the maintained, general-purpose Android tablet
remains the foundation. Crestron is an optional role. The native-panel question
means a setup interface that selects one use/application and then runs it full-screen,
not several applications displayed simultaneously.

## Decision

Build **one current-Android/current-kernel platform**, with two independently testable
Crestron paths on top:

1. **Supported client panel:** a mode manager launches Home, Go, ONE or a web project,
   using the appropriate supported Android runtime. This is the implementation-ready
   route to useful panel behavior after the Android port is functional.
2. **Native runtime compatibility:** investigate running Crestron's actual panel APKs
   against a ported or reimplemented panel service layer. Static inspection found
   concrete service boundaries, so this is a credible prototype candidate. It is
   not demonstrated native-panel equivalence and should not block the Android port.

Do not transplant an entire old Crestron firmware image as the maintained OS. The
selected current-kernel direction remains intact. If the native services can be
ported, keep them in an optional compatibility package with explicit dependencies.
“Runs any Crestron application” cannot be promised: project runtimes, scheduling,
partner applications and management integrations have different requirements.

## What was actually inspected

Read official Crestron product/manual/SDK pages, the public app and firmware update
manifests, and three actual application archives. No applications were executed,
installed, patched or repackaged. No physical device or lab processor was accessed.

The [official application manifest](https://crestrondevicefiles.blob.core.windows.net/70-series/production/applications/manifest_x70_apps.json)
is saved under `evidence/crestron/`. The exact URL is documented in official
[TSW-70 release notes](https://www.crestron.com/release_notes/tsw-xx70_2.004.1029.001_release_notes.pdf).
Archive URLs, sizes and SHA-256 pins are in `downloads.lock.json`; extracted
manifests and `apk-inspection.json` preserve the static findings.

- HTML5 display host: **com.crestron.blackbird 1.3.0.172**, minimum API 26,
  target API 28. Archive 18,308,273 bytes.
- General Web: **com.crestron.generalweb 1.02.017**, minimum API 24, target API 24.
  Archive 6,485,786 bytes.
- Home panel: **com.crestron.phoenix.touchscreen 4.12.18+tswr**, minimum API 21,
  target API 35. Archive 58,207,482 bytes.

All three inspected archives contain APK native libraries only for **armeabi-v7a**.
These particular panel binaries therefore need ARM32 userspace/native-library
support, even on an ARM64 kernel. This is not a reason to use a 32-bit kernel.
Do not equate these panel APK requirements with the different Play Store packages.
Minimum SDK alone also does not establish installation or runtime compatibility on
Android 17; old target-SDK behavior, linker namespaces and platform APIs need testing.

The ZIPs also contain detached `.sig` files. Their cryptographic authenticity was
not independently verified. Download provenance and content hashes were recorded;
neither the APKs nor extracted proprietary libraries are committed to this repository.

## Why native panel APKs are not self-contained tablet apps

These are direct static observations, not a guessed hardware-identity restriction:

- The HTML5 host's `CresStoreWrapper` static initializer loads **cresstore_jsonJNI**.
  The corresponding `libcresstore_jsonJNI.so` is not in the APK. `CresStoreManager.init`
  calls its wrapper creation path, and the code explicitly handles missing-library errors.
- Its `SecureStorageWrapper` loads **SecureStorageJNI**, also absent from the APK.
  This is a platform service dependency, not Android's ordinary app preferences.
- `SignalTransportFactory` initializes the Crestron interfaces and connects its
  Iplink client to **127.0.0.1**. That is a local panel-service connection, not the
  remote CP4 control-system address.
- General Web's constructor creates that same signal transport and exposes its
  state to its WebView. It has an explicit missing-library failure path. Its code
  also accommodates a panel-provided client certificate at `/dev/shm/client.pem`;
  this does not prove a mandatory per-device certificate restriction.
- The Home panel APK also loads `cresstore_jsonJNI` and uses a localhost signal
  transport. Home panel mode is therefore a distinct integration task from
  installing **com.crestron.phoenix.app**, the normal Home mobile app.

Class names, observable load calls, bundled library inventory and disassembly hashes
are recorded in `apk-inspection.json`. Full selected disassembly remains in ignored
`work/crestron/` and can be regenerated using the inspector script. A missing
required native-library implementation is a concrete obstacle to an unmodified
APK running its panel paths on ordinary AOSP; it is not proof a replacement is impossible.
No runtime failure has been observed because no APK was run.

The inspected manifests do not establish that installing these APKs requires a
Crestron platform signing key. Likewise no mandatory hardware-ID binding, secure-boot
restriction on the Fire, or licensing obstacle to all native functions was demonstrated.
Those should remain open questions until corresponding code or test evidence exists.

## What supported Android clients already cover

**Home:** the normal Home Android client is the sufficient route for the user's
Home requirement, subject to full feature testing. Its currently inspected Play
metadata requires Android 8.0. It is not a general custom-SIMPL project runtime.
See the existing Home evidence in `evidence/crestron-play.json`.

**Smart Graphics:** [Crestron Go Android](https://www.crestron.com/Products/Catalog/Control-and-Management/Software/Programming-Commissioning/CRESTRON-GO-ANDROID)
supports programmed Smart Graphics interfaces, Android 11+, H.264/MJPEG camera
streams, and compatible 3-Series/4-Series/VC-4 systems. Use the mobile project
target and test joins/extenders; do not promise every native-panel binary project
can be copied unchanged. The Android-specific page does not establish full Rava
parity; a cross-platform security guide says feature availability is OS dependent.

**HTML5/Construct:** [Crestron ONE Android](https://docs.crestron.com/en-us/9580/Content/Topics/Configuration/Configuration.htm)
supports CH5/Construct projects on Android 14+. Deployment uses a `.ch5z` mobile
project uploaded to the processor as **CH5 Mobile**, then configured in ONE. That
differs from uploading a native touch-panel project directly to a panel in Toolbox.

**Web projects:** [Web XPanel integration](https://sdkcon78221.crestron.com/sdk/Crestron_HTML5UI/Content/Topics/Platforms/X-Custom.htm)
provides a documented browser connection to a processor. It must be enabled in the
project and uses WebSocket/authentication configuration. Merely opening a native-only
CH5 bundle in a browser is not equivalent. The SDK explicitly distinguishes this
connection from a panel's native communication bridge.

**Single selected application:** an Android launcher/device-policy component can
store the chosen mode and manage startup, full-screen presentation, administrator
access and crash recovery. Android documents [lock task mode](https://developer.android.com/work/dpc/dedicated-devices/lock-task-mode)
and allowlisted applications. This is an engineering route, not an implemented
FireTabs component. Optional panel role must preserve a deliberate return to ordinary
tablet use. One foreground mode can still have necessary background services.

Found existing [CrestronKeeper](https://github.com/akellai/CrestronKeeper) code and
inspected commit `6546f94d2864614c8cc5ca069fad0c39b3b75f69`. It restarts/foregrounds
the old `air.com.crestron.andros` application. It is a lifecycle-reference project,
not a native panel runtime or a ready-made current-Android mode manager.
A [CH5 PWA demo](https://github.com/jphillipsCrestron/ch5-pwa-demo) is another useful
reference for installed web presentation. Neither project was built or run here.

## Media, intercom, scheduling and management distinctions

**Video:** Crestron's [CH5 video architecture](https://sdkcon78221.crestron.com/sdk/Crestron_HTML5UI/Content/Topics/UI-Video-Considerations.htm)
uses native decoding and a video surface coordinated with HTML rendering. Native
RTSP behavior cannot be inferred from ordinary HTML video support. Browser and
native paths must be tested independently with actual stream formats/authentication.
Using an explicit stream gateway could be a separate option, but is not equivalent
to directly reproducing the native component.

**Intercom:** Rava/SIP ringing, answering, microphone/speaker routing, echo handling,
background wake and any video must be acceptance tests. Do not infer Android ONE or
Go has identical intercom behavior to a TSW from an iOS guide or a shared product name.
The native host's TSW adapters expose intercom/system functions, but that does not
establish which services will be portable. Full parity is unresolved.

**Scheduling/partner apps:** the native manifest includes third-party packages as
well as Crestron packages. Some providers offer ordinary Android/web deployments;
others depend on their device program or panel integration. For example,
[Microsoft certifies particular Teams panel hardware](https://learn.microsoft.com/en-us/microsoftteams/devices/teams-panels-certified-hardware);
copying its APK does not certify a Fire tablet. [Zoom offers consumer Android
controller deployment](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0068512),
but its [published hardware requirements](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0059373)
include a 1.5 GHz dual-core CPU and screen-size requirements; douglas is specified
at 1.3 GHz. Do not claim it meets every vendor's requirements merely because Android
is recent. Partner mode compatibility needs a separate per-application result.

**Native management:** Toolbox discovery/project upload, a panel IP table, web setup,
console commands, firmware management and XiO Cloud identity are additional behaviors.
Successful control from a mobile client proves none of those native management paths.
They should be explicit optional compatibility targets, not implied by the mode selector.
The core native-rendering proof need not wait for every management feature.

**Licensing correction:** the current [Crestron licensing portal](https://www.crestron.com/Support/Tools/Licensing-Registration/Licensing-Portal)
says the ONE/HTML5 mobility license is no longer required with current software.
Older SW-MOBILITY pages and release notes are historical. Do not add that old license
as a blanket blocker. Other app purchases, provider subscriptions and rights to
redistribute proprietary software remain separate; no conclusion about those rights
was established by downloading public update files.

## Native dependencies: the next specific gate

The public [TSW-70 firmware manifest](https://crestrondevicefiles.blob.core.windows.net/70-series/production/firmware/manifest_x70_firmware.json)
currently advertises `tsw-xx70_3.003.0021.001.puf`. An HTTP HEAD request to its exact
`devicefiles.crestron.io` URL returned **404**. A separately tested older
`3.001.0020.001` URL also returned 404. This is an unavailable tested download,
not proof no firmware exists or that dealer/authorized downloads cannot supply it.
Headers are preserved. No full PUF was downloaded.

Crestron's [open-source page](https://www.crestron.com/legal/open-source-software)
lists component sources and a 581 MB Amlogic Android 5 BSP archive for older x60
hardware. This does not establish availability of a buildable TSW-70 panel runtime.
It was not downloaded, and no public buildable implementation of the missing native
panel services was found in the inspected sources/search. Package dependencies still
need full-firmware or read-only lab-panel inventory.

The concrete next native milestone is therefore:

1. Obtain an available authorized firmware package or user-supplied read-only lab
   inventory; identify the two JNI libraries, their ELF dependencies, Java framework
   components and local service executables/configuration.
2. Classify each dependency as portable unmodified binary, rebuildable source,
   documented interface to reimplement, or unresolved hardware-specific component.
   Determine library visibility and ARM32/ARM64 requirements on current Android.
3. Test the unmodified HTML5 host in an isolated compatible Android environment,
   recording missing libraries/services and startup progress. Start with project
   rendering and digital/analog/string join round trips to the lab CP4, then add
   media and intercom. This tests the real native path, not just a launcher UI.
4. If a service adapter can satisfy those contracts, package it independently of
   the Fire kernel and test native Home mode and selected additional modes. Unsupported
   functions must report honest capability/error results; stub success is not parity.

No compatible emulator is configured in this session, and no emulator system image
was downloaded. Before larger firmware/BSP/emulator downloads, report size and disk
requirements. Read-only lab comparison does not authorize changes to the Fire tablet,
the lab touch panel, the processor or its programs.

## Acceptance and project boundaries

There are separate pass criteria for **Android platform**, **mode manager**,
**supported mobile/web clients**, **native rendering/control**, **native media/intercom**,
and **native management**. A result in one does not imply success in the others.

The recommended direction is to implement useful single-mode behavior with supported
clients while retaining a concrete native-runtime compatibility experiment. The native
track is neither dismissed nor allowed to force the general-purpose OS back onto an
obsolete Crestron firmware base. At present its first gate is obtaining and auditing
the missing panel service layer, not the Fire CPU's ability to execute Android APKs.
