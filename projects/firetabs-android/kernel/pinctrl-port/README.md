# MT8163 pinctrl/EINT candidate — issue #19

ACK target: d9318bdb4c34e8b2d997b4f67ced56b120b22b87.
Donor: bengris32/linux-f 20951722df6ae1f6fecbfcea0a7d585118a06f3f.

Three unmodified donor files provide the real driver, pin descriptors and DT
function IDs. Original GPL headers/copyrights are retained. `inputs.json` maps
each overlay file to original hash-verified evidence; pinned ACK API and build
references are under `evidence/pinctrl-port` with URL/hash provenance.

The descriptor table has 155 unique numbered pins (0–154). The driver declares
six EINT ports, 169 AP interrupts and 64 debounce entries, with the MT2701
hardware debounce table. These are donor declarations, not measured tablet
properties. The common probe API, data fields and special pull/IES/SMT helpers
are present in the pinned ACK. No common implementation is replaced and no pin
or EINT numbering is changed. Board electrical routing remains unverified.

`apply_pinctrl_port.py` checks source revision, original hashes, absent targets
and patch applicability before changing a disposable checkout. The isolated
Linux `pinctrl-probe.yml` compiles the MediaTek pinctrl directory with W=1,
verifies PINCTRL_MT8163=y, then inspects the actual MT8163 object ELF and hashes.
It deliberately stops before a full Image; it cannot complete #19 by itself.
It uses a shallow ACK fetch with the same 3 GiB post-transfer Git-storage budget,
15 GiB free-disk/7 GiB RAM preflight and a 15 minute timeout. Transfer bytes are
not bounded by the post-transfer storage check. No paid runner is provisioned.

Pending: compiler result; comparison against legacy pin/register/EINT mappings
and actual douglas consumers; full DT schema work (#27); full Image integration
with clock providers (#18); all hardware tests. No installable firmware, physical
operations or runtime qualification are provided.
