# MT8163 watchdog provider binding — #27

This source-matched proposal extends the pinned ACK watchdog schema to the exact
MT8163 compatible already supported by the cached donor driver. It leaves all
other SoC constraints unchanged and restricts MT8163 timeout-sec to the driver's
2..31second range. It does not change the DTB, watchdog driver or device state.

## Reused hardware knowledge and probe contract

The donor is84fae418d21ba2f7b92215834cfe4708305954c8; source SHA256
39f0d5ada7e66bc8e62b15b8776c76df3265ab8fa64ccd50a2b3c28ae814a407.
Its MT8163 descriptor registers15 reset lines, matching the retained reset header.
Five register offsets and four keys agree with the legacy Git-object header at
e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74. This is concrete reuse of the old
mapping; it is not proof that every register bit, sequence or reset works.

Probe maps resource0, optionally requests IRQ0 with IRQF_NO_AUTOEN, initializes
watchdog policy, registers the watchdog and then enables the bark IRQ when
present. It registers the reset controller using the descriptor count15. Reset
IDs map directly without a SoC remapping table or swsysrst-enable capability.
The legacy/modern bit5 naming differs, but the modern macro is unused in the
cached file; that naming difference alone is not a behavior change.

If hardware reports the watchdog already enabled, mtk_wdt_init invokes start,
which programs timeout/reload/mode. Therefore candidate boot/probe is not passive
observation. Nothing here qualifies an independent failed-boot return path,
watchdog timing, external reset output, bark IRQ delivery or reset consumers.

## Validation

The opt-in locked profile is
projects/firetabs-android/kernel/dtb/bindings/mt8163-watchdog.json. It is applied
only to an isolated extracted corpus, with original/patch/proposed hashes checked.
The baseline DTB remains SHA256
b837e6cb439d43778527c834e534abddb271170fd29cb6b13b174272214d1411.

The decoded candidate watchdog node passes19 actual Draft201909/typeSize controls:
missing/wrong compatible, reg count, IRQ count, reset cells, unknown property and
MT8163 timeout bounds are tested; optional IRQ/provider properties and existing
SoC policies remain valid. Property mutations use decoded DT cell representation.
Sparse source facts and all input hashes are retained in evidence/watchdog-binding.

The full matched context has **41 diagnostics**:29 unmatched and12 validation.
Exactly one watchdog unmatched diagnostic is removed from the retained42 baseline;
no diagnostics are added. The wrapper still exits1 and passed remains false.
No diagnostic is hidden to obtain a pass.

```sh
work/dtb-tool/venv/bin/python evidence/watchdog-binding/check-controls.py
python3 -m unittest discover -s tests -p test_watchdog_binding.py -v
```

The full wrapper command is retained in evidence/watchdog-binding/report.json
with the temporary corpus path normalized. Reuse out/watchdog-command.json for
an executable local argv against the cached archive; no new download is needed.
Next ready #27 source scope: pinctrl syscfg-parent resources and matching binding,
with actual decoded-node controls. Runtime reset/recovery gates remain open.
