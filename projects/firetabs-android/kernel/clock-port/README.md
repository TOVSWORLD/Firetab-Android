# Experimental MT8163 clock overlay — issue #18

Target: ACK `d9318bdb4c34e8b2d997b4f67ced56b120b22b87`.
Donor: bengris32/linux-f `20951722df6ae1f6fecbfcea0a7d585118a06f3f`.

The overlay contains nine real donor drivers and eleven clock/reset binding
headers, retaining original GPL SPDX and copyright notices. `inputs.json` maps
files to locally hash-verified original evidence. The original three base drivers
are in `evidence/kernel-audit/bengris7`; the six subsystem drivers and pinned ACK
API/build references are in `evidence/clock-port`, with URL/SHA-256 provenance.
No register addresses, parent names or binding IDs are renumbered by this overlay.
The build wiring patch adds the donor's seven configuration symbols and nine
objects to ACK; it does not replace the MediaTek common implementation.

Corrections to donor lifecycle behavior:

- apmixedsys and infracfg probes save `clk_data` with `platform_set_drvdata`,
  matching their existing removal paths and ACK's common probe implementation.
- apmixedsys removal unregisters the gates registered by its probe.
- infracfg registers its existing six fixed factors before composites, with
  reverse-order cleanup on probe failure/removal. The legacy MT8163 clock driver
  also registers this factor table (see `evidence/kernel-audit/legacy/drivers/clk/mediatek/clk-mt8163.c`).

The factor table includes `osc_ck`, `osc_d8`, `osc_d16`, `clk26m_d8`, `eth_d2`
and `onfi_d2`; these are actual donor/legacy clock definitions, not placeholders
for missing providers. Hardware validity of the inherited values is untested.

`python3 scripts/apply_clock_port.py PATH_TO_DISPOSABLE_ACK` checks the revision,
source hashes, existing destinations and patch context before applying. It
modifies only that disposable checkout and refuses an already applied overlay.
`bash scripts/build_ack_baseline.sh clocks` fetches the same shallow ACK source,
selects all seven clock symbols, verifies they resolve to `y`, builds the
MediaTek clock directory with W=1, then links a full generic ARM64 Image/vmlinux.
This remains a generic configuration with experimental MT8163 providers, not a
complete douglas configuration. W=1 diagnostics must be reviewed; no warnings
are suppressed. The compiler and host dependencies remain runner-provided.

Pending: actual compilation result; exhaustive DT consumer/parent-name/ID review;
matching full binding-schema validation; register/critical-clock audit; physical
clock rates/reset behavior. This work does not complete #18 or any runtime gate.
No firmware packaging or device operations are performed.

First Linux compile (run 40168938776) failed on donor `MUX_GATE_UPD_FLAGS`,
`MUX_GATE_UPD` and `MUX_DIV_GATE_FLAGS`, absent from ACK. `mux-api.patch`
backports the donor's actual direct-register read/modify/write + update-bit
operations and initializer macros, retaining ACK's existing set/clear ops and
allocation APIs. Using set/clear ops with zero set/clear offsets would be wrong.
The audio driver retains donor composite flags=0 through a local initializer;
ACK's ordinary MUX_DIV_GATE forces CLK_SET_RATE_PARENT and is not equivalent.
New donor common-source references are hash-recorded in evidence/clock-port.

## Bounded reference review

Run `python3 scripts/audit_clock_references.py`. The committed report records
numeric header identifiers mentioned in each provider source; this is a textual
cross-check, not proof of successful clock registration or a full DT consumer
mapping. Board DT supplies the external `clk26m` and `clk32k` names.

Three literal parents remain unresolved: `apll2_div0`, `apll2_div1` (MM HDMI audio
and SPDIF gates), and `hdmitx_dig_cts` (top HDMI CTS factors). The legacy driver
has two 1:1 APLL aliases and an HDMI CTS parent chained to `clk_null`; these are
not evidence of a functioning hardware clock path. No aliases or dummy CTS
source are added by this port. Determine actual ownership/rates if these HDMI
paths are needed; their impact on the tablet's integrated display is untested.
These gaps prevent claiming a complete hardware clock implementation despite
successful object compilation. Full matched binding/schema validation is #27.

The audit also maps 102 literal named DT clock references in the captured source
files to the expected provider's header and numeric ID. It fails on unknown
provider labels or IDs. This does not expand arbitrary DTS/C expressions or
validate live providers, mux routing, clock rates or schemas. Use `--check` to
compare the recomputed report with the committed evidence.

## MMSYS parent integration (#18)

`mmsys-parent.patch` adds the exact pinned donor SoC match and descriptor to
ACK's existing MMSYS parent, enabling creation of `clk-mt8163-mm`. The matched
routing and reset headers retain their original SPDX terms; provenance and
hashes are in `evidence/clock-port/mmsys-parent/integration.json`. The existing
parent and patch are verified before mutation and the patched result afterward.

The captured disabled DSI node already uses compact reset ID23. The donor's
MT8163 descriptor incorrectly interprets it as raw bit23 (PWM); integration uses
the34-entry mapping so DSI resolves to bit24. LCM's donor bank2 resolves to0x148,
but pinned legacy source locates LCM at0x150; the overlay corrects it to bank4.
Original donor evidence is retained unchanged, and the adapted overlay is hashed.
No new DT reset consumers are introduced. Routing covers only the donor's minimal internal display path;
external routes are absent. The generic build explicitly enables MTK_MMSYS and
compiles its parent object before linking Image. Explicit MMSYS parent object, full generic Image and QEMU diagnostic smoke
passed at5c02907 in run40763077737. Compile result and unchanged-input receipts
are in evidence/clock-port/mmsys-parent. Actual probe, routing and reset behavior
remain untested.
