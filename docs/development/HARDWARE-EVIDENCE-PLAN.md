# Douglas hardware identification and mode/return evidence plan

This is a source/evidence plan, not an opening, probing or shorting procedure.
Owner hardware access is acceptable if needed for planning. Automatic runs retain
no-device-access restrictions. No owner physical action is requested here.

The [firsthand 2020 cover-removal account](https://sakue.com/archives/821) labels
its device 2017/7th-generation/KFDOWI and reports exterior code SX034QT. It is a
useful same-generation mechanical reference, but does not identify our PCB
revision, UART pads, voltage or safe BootROM contact. The
[iFixit 7th-generation category](https://www.ifixit.com/Device/Kindle_Fire_HD_8)
helps prevent generation mixups; it is not an electrical capture procedure.
Do not substitute 2018/8th-generation board images. The
[source inventory](../../evidence/hardware-identification-plan/report.json)
records these limited claims without copying photos or personal identifiers.

The smallest future evidence collection should proceed in separate scopes:

1. Establish existing model/revision provenance and match source photographs to
   that revision. Exclude serial/barcode/household data from public records.
2. Qualify a model-specific power/battery isolation and mechanical inspection
   plan before proposing opening. Record board geometry/revision separately from
   any UART or BootROM contact claim. No electrical contact is part of identification.
3. Establish ground/reference and UART electrical level/routing from traceable
   evidence. SoC GPIO79/80 are not PCB pad numbers. A USB adapter's advertised
   capability does not establish the tablet's signaling voltage.
4. Qualify entry and failure exit before any mode-changing attempt. Distinguish
   ordinary reset, named RTC-changing modes, BootROM entry, payload execution and
   storage/security modification using existing source-effect receipts.
5. Qualify bounded log acquisition and retrieval separately from diagnostic loading.
   Publish only sanitized fixed markers/metadata after provenance checks; no
   black-screen or queued-byte observation substitutes for captured boot progress.

Stop progression at missing evidence; do not turn this list into operating steps.
Original user/boot-region escrow, RTC state where affected, reachable restoration,
security acceptance and safe memory placement remain independent requirements.
The original loader/recovery issue #106 remains open. Next source investigation
is same-generation internal-board/battery-isolation provenance, followed by a
concrete reviewable owner inspection proposal only when those facts are sufficient.

## Exact-board isolation evidence gap (#301)

The [supplier's seventh-generation battery page](https://www.ifixit.com/products/amazon-fire-hd-8-7th-gen-replacement-battery)
provides compatibility/specifications, not an exact-PCB connector isolation
procedure. Battery nominal voltage is not UART logic voltage. Mixed-generation
third-party replacement manuals were excluded as electrical-procedure evidence.
The public FCC index request returned HTTP403 and was not inspected; that access
failure does not prove missing documentation. The existing firsthand cover-only
account still does not establish our board revision or electrical isolation.

The owner has been asked only whether internal-board photos or PCB revision
records already exist from an earlier opening. No new opening, connection,
measurement or probing is requested. Existing records could resolve board matching
without another physical step; any later sharing must omit serial/barcode and
household information. Do not infer a connector technique or voltage from a
similar model. The [source-gap receipt](../../evidence/board-isolation-evidence-gap/report.json)
records this exact missing information and source limits.

Until board identity/isolation evidence is qualified, keep a physical inspection
proposal incomplete and continue independent source work. Initial security,
recoverable entry/exit, original-state restoration and usable real logs remain
open, regardless of battery compatibility or the host agent's passing tests.
