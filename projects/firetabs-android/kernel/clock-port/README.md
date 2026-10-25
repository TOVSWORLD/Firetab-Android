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
