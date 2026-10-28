# Cached LK CPU-node removal and frequency cap — #347

Exact-OTA LK SHA256:
4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08.
Selected static source evidence only; no firmware/helper execution or device read.

## Selected behavior

The caller guard loads GOT+0x310, pinned nonzero Thumb pointer0x4bd258ed, and
calls0x258ec atpayload0x3e076. It is a function-presence guard, not demonstrated
runtime callback selection. The function locates `/cpus`, walks child nodes and
matches device_type=cpu. It reads the first big-endian reg cell and compares its
low8 bits with a limit. IDs at or above that limit select node-removal helper
0x46c74 (structure-end calculation and splice), rather than setting status to
disabled. The bit8 cluster case logs an unknown-type warning; general multi-
cluster topology support is not qualified by this trace.

Core limits come from bits4..7 of helper0x4b014(argument3): selectors8..14 map
through the pinned table atpayload0x5ef20 to3,4,4,4,2,4,1. Other selectors use4.
The frequency helper0x25794 reads the same helper separately. Its low nibble
selects2,000,000,000Hz for0 or1, decreases by100,000,000Hz per step through10,
and uses1,100,000,000Hz above10. A retained node's clock-frequency property is
written only if its current value exceeds the selected cap. This is a DT cap,
not measurement or proof of the running clock, OPP safety or actual online CPUs.

The host model takes the two input words separately. Stability between reads,
actual helper values, missing/malformed properties and nonstandard CPU reg
encodings remain unqualified. The selected callback does not establish a PSCI
or enable-method rewrite. CPU deletion/frequency limiting cannot substitute for
qualifying the maintained kernel's CPU-start and secure-monitor contracts.

## Reproduce and continue

```sh
python3 scripts/trace_lk_cpu_fixup.py \
  --lk out/ota-loader-inspection-659664620/lk.bin \
  --output out/lk-cpu-fixup-fresh
python3 -m unittest discover -s tests -p test_lk_cpu_fixup.py -v
```

Evidence/lk-cpu-fixup contains complete selected function/window hashes, table,
call/literal receipts, bounded disassembly and sparse replay data. Five tests
cover all16 core/frequency selectors, keep/remove thresholds, downward-only
caps, separate reads, cluster-bit exposure and drift rejection. The analysis
object remains ET_REL without entry/program headers and is never executed.

Next executable #347 source acceptance: consolidate a finite final-DTB mutation
and entry/handoff coverage inventory across the pinned receipts, explicitly list
unresolved dispatcher setup and trust boundaries, and identify the minimum
missing evidence for installed LK3 compatibility. Do not infer physical loading,
independent failure return or retained-log qualification from these source tests.
