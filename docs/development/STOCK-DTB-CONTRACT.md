# Candidate appended DT contract — issue #21

The model-verified OTA candidate from #46 contains a wrapped gzip kernel followed
by two concatenated DTBs. This is actual file evidence, stronger than assuming
the donor tree matches firmware. Candidate identity/authentication and installed-
build limitations remain in [STOCK-OTA-INSPECTION.md](STOCK-OTA-INSPECTION.md).
No binary artifact is published and nothing is booted or modified on a tablet.
CI exercises synthetic inputs only; the actual candidate inspection was a local
read-only run with the retained hashes and pinned fdtget version.

Reproduce from the already extracted, hash-pinned local boot.img with pinned
DTC 1.8.1/fdtget tooling. Use a fresh output directory:

```sh
python3 scripts/inspect_stock_dtb.py out/stock-ota-douglas-659664620/boot.img \
  --expected-sha256 8982fa50193acc764be69ee51027ee92e83614cee4b8235b07439d1f9e2db363 \
  --output out/stock-dtb-659664620
```

This downloads nothing. It checks the local boot-header layout, observed 512-byte
kernel prefix, gzip checksum and a 64 MiB decompression cap while streaming output
in 64 KiB chunks. It retains the decompressed hash/prefix and validates bounded
contiguous DTB headers/sizes/reservation-map termination; unknown suffix data is
rejected. At most 32 DTBs, each <=2 MiB, and 128 selected fdtget queries per tree are
allowed. fdtget checks the actual tree while reading only selected public
properties. This is layout inspection, not full schema validation, signature
verification or proof of firmware/kernel API behavior. Outputs are ignored local
DTBs/report; input checksum matching authenticates no external certificate.

## Actual layout and variants

The gzip member occupies 7,026,236 bytes and decompresses to 16,584,856 bytes,
SHA256 43b5e6440ad70a6622e3d4ee9cb92f3207d45707e54a16697430036080f2f6e0.
The remaining 164,918 bytes are exactly two DTBs, with no unclassified suffix:

- Index 0, root version `pre_evt`: 82,277 bytes, SHA256
  176c96a8f36c44d00340b428eab0a9cc0ca7e8f20b79d4903a24eb003d718498.
- Index 1, root version `hvt`: 82,641 bytes, SHA256
  887392afe3b005b9324f0797f124153ed846649b0ebdba86f2018f1caf6c9da1.

Both root model/compatible values are MT8163/mediatek,mt8163, not a per-variant
Amazon marketing identity. The OTA's target properties provide the KFDOWI/douglas
identity. Which DTB is selected and whether the loader changes its version or
other properties remain unknown. The stock-facts collector now includes the
individual raw `/proc/device-tree/version` property to help distinguish runtime
selection later; no real collector/device transport was executed.

## Memory and reservations

Both DTBs have two address/two size cells and
`memory@00000000/reg = <0 0x40000000 0 0x20000000>`: a static 512 MiB range.
This does not measure usable RAM or refute the hardware's 1.5 GiB specification.
It reinforces why loader/runtime memory fixups must be collected before changing
the new DT. Both have empty header reservation maps and these body nodes:

- ATF at 0x43000000, size 0x30000 (192 KiB), no-map.
- RAM console at 0x44400000, size 0x200000 (2 MiB).
- mdump at 0x4bd00000, size 0x300000 (3 MiB).
- Low-level log at 0x44600000, size 0x20000 (128 KiB). Its node is misleadingly
  named ll_log-reserved-memory@46600000; the reg value is authoritative here.
- Dynamic CONSYS reservation, size/alignment 0x200000, no-map, no fixed address
  established by this file inspection.

These match the previously audited legacy source declarations and corroborate
that the newer donor's omitted reservations require explicit review. Preserve
this evidence rather than blindly enlarging RAM or discarding firmware regions.
Runtime placement/usage and ACK driver compatibility are still unverified.

## CPU firmware interface

Both declare `/psci/compatible = arm,psci`, method=smc and explicit function IDs
cpu_suspend=0x84000001, cpu_off=0x84000002, cpu_on=0x84000003,
affinity_info=0x84000004. CPU 0 enable-method is `mt-boot`, agreeing with the
legacy custom CPU/MTCMOS path. The donor changes the method to generic psci and
the firmware compatible to arm,psci-0.2. Pinned ACK supports legacy explicit-ID
PSCI as reviewed in [DOUGLAS-BOOT-CONTRACT.md](DOUGLAS-BOOT-CONTRACT.md); an updated
kernel does not inherently require replacing this firmware interface.

The files do not prove firmware lacks PSCI 0.2, nor that ACK CPU_ON can replace
legacy MTCMOS sequencing. Do not use the donor's newer compatible as proof that
PSCI_VERSION is implemented. No boot configuration is changed from these facts;
a future isolated legacy-PSCI-compatible candidate and single-CPU diagnostic
policy still need deliberate review and the qualified loader/log/recovery path.

Exact component/DT offsets, hashes, selected raw values, inspector hash and
tool version are in evidence/stock-dtb/candidate-report.json. This advances the
static contract audit; installed-build matching, runtime memory, CPU behavior,
boot-image authentication, recoverable execution and logs remain open in #21.
