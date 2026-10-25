# Roadmap

This is a prioritized set of evidence gates, not a delivery promise or completed design.
Live issues own work status; project validation files own executed-test status.

## FireTabs Android

1. Select a maintained Android-compatible kernel candidate through a source-based
   MT8163/douglas hardware and interface audit. Preserve reusable upstream work.
2. Establish a pinned Linux kernel build and essential board bring-up evidence.
3. Integrate Android 17 hardware interfaces and prove boot, graphics and networking.
4. Validate present hardware, enforcing security, updates and everyday workloads.
5. Consider supported/long-term release status only with a measured test matrix and
   funded/named maintenance capacity.

## Crestron Panel

1. Define the full Home/mobile client acceptance matrix against the lab's exact processor.
2. Once an appropriate Android platform exists, implement selected-mode lifecycle and
   validate supported clients independently of native panel compatibility.
3. Inventory native runtime services and JNI dependencies from authorized sources.
4. Demonstrate a real native project with bidirectional feedback before widening parity
   claims; add media/intercom/deployment/management claims only after individual tests.

## Shared repository

Maintain reproducible evidence, contribution review, issue hierarchy, release manifests
and source/security/license inventories. Do not consume large build resources or publish
binaries merely to meet the monthly calendar. General-purpose use remains the Android
scope; the optional panel project does not replace it.
