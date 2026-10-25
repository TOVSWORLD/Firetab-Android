# MT8163 PMIC wrapper and power-domain candidate — issue #20

Target ACK: d9318bdb4c34e8b2d997b4f67ced56b120b22b87.
Donor: bengris32/linux-f 20951722df6ae1f6fecbfcea0a7d585118a06f3f.
Original GPL notices are retained in source evidence and the overlay.

`provider.patch` adds the donor's MT8163 wrapper register table, type/cases and
compatible data; initialization reuses existing MT2701 helpers as the donor does.
The patch adds only the MT8163 header and match entry to the ACK power-domain
core, plus MT8163 bus-protection masks. The new domain table/binding has eight
real domains. No unrelated hardware-voter/SMC/MT8196 implementation is imported.
ACK's existing common power-domain implementation and bus-protection polling
remain active. No inert provider or protection bypass is introduced.

Pinned original target/donor references and hashes are in evidence/power-port;
`inputs.json` maps the two overlay headers to their original captured sources.
The legacy wrapper header is read from its pinned Git object, not inferred from
a potentially case-collided checkout. Its register-offset comparison is recorded
separately; offset agreement alone does not verify initialization transactions.

`build_power_probe.sh` performs an isolated Linux W=1 build of the actual wrapper
and common power-domain objects with MTK_PMIC_WRAP=y and
MTK_SCPSYS_PM_DOMAINS=y, recording ELF architecture, compiler identity and hashes.
This probe does not link a full Image or execute driver probe/power transitions.
It has a 15 minute timeout and the same source/resource gates as the prior
object probe: shallow single-commit fetch, 3 GiB post-fetch Git-storage budget,
15 GiB free disk and 7 GiB RAM. Transfer bytes are not bounded by Git storage.
No paid resources or physical tablet operations are used.

Pending: compiler result; matched DT binding validation (#27); full Image with
clocks/pinctrl; wrapper/reset/PMIC supplies and clock ordering; bus-protection
mask/power sequence review against legacy; all hardware read/write and voltage
qualification. The common API compiling does not establish safe runtime power
sequencing. Keep #20 open until its remaining acceptance work is accounted for.
