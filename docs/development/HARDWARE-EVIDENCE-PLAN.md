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

On 2026-10-27 the owner confirmed there are no existing internal-board photos or
PCB revision records. This question is resolved; do not ask it again. Hardware
access remains acceptable for planning, but no specific opening, isolation,
connection or measurement has been authorized or qualified. The existing
[source-gap receipt](../../evidence/board-isolation-evidence-gap/report.json)
records the earlier source limits; this owner answer supersedes its pending-question
state. Do not infer connector technique or UART voltage from a similar model.

Next independently qualify exact-generation mechanical/isolation evidence and
prepare a reviewable inspection proposal with explicit scope and stop conditions.
Do not present electrical contacts, shorts or mode changes as identification steps.
If adequate evidence remains unavailable, state that specific source blocker;
absence of old photos is no longer a reason to wait for the owner.
Until board identity/isolation evidence is qualified, keep a physical inspection
proposal incomplete and continue independent source work. Initial security,
recoverable entry/exit, original-state restoration and usable real logs remain
open, regardless of battery compatibility or the host agent's passing tests.

## Owner-review proposal: cover-only identification (#345)

**Review artifact only. Opening is not approved or qualified for this exact unit.**
The decision requested is whether this limited scope is suitable for a competent
operator to assess; it is not approval for electrical work or recovery execution.
No physical step is performed by automation.

### Purpose and proposed deliverable

Obtain one overall interior view and any PCB revision marking visible without
moving a connector, shield, battery, ribbon or board. This would resolve whether
our unit matches the source layout and what exact connector evidence is still
needed. If markings are hidden, an incomplete identification is the correct result;
do not expand the operation to uncover them. No photos or records already exist,
as confirmed by the owner; that question is resolved.

### Source basis and limits

- The [firsthand cover-only account](https://sakue.com/archives/821) explicitly
  names 2017/KFDOWI/SX034QT and shows case clips and an interior view. It supports
  a model-family mechanical reference, not our revision or a guaranteed opening
  method. It reports no cover adhesive on that particular unit.
- The [supplier demonstration](https://www.youtube.com/watch?v=oZjys6q6BRA) was
  actually viewed at 2:33, 3:24, 3:29 and 4:15. The gross board/battery/speaker
  arrangement is broadly consistent with the independent photo. Its title names
  Fire HD8 seventh generation while its description names an Asus model; this
  unresolved discrepancy prevents treating it as a verified connector procedure.
  Its battery-removal section is outside this proposal.
- The [repair-provider guide](https://www.lmlrepair.com/guides/tablet/amazon/kindle/kindle-fire-hd-8-7th-gen/power-button-repair)
  has generic heating/disconnection directions without exact connector geometry.
  Do not adopt those directions to fill this gap. No temperature, insertion depth,
  force, connector direction or electrical contact is established here.

### Scope for review

A person experienced with tablet mechanical inspection must first assess whether
cover-only observation is feasible using the exact-generation references and the
actual unit's condition. A powered-off tablet still contains an energized battery;
this proposal does not claim electrical isolation. If the operator needs an
unverified connector action to make their work safe, stop and resolve that method
before any opening. This document is not a substitute for a qualified mechanical
procedure or an operator's own assessment.

No battery disconnection/removal, board/shield removal, test-pad contact, soldering,
shorting, voltage injection, USB/charger/UART connection, mode change, unlock,
reboot experiment or firmware/helper execution is in scope. No purchases or repair
booking are authorized. No approach is selected merely because a video shows it.

### Stop conditions and evidence handling

Stop for battery swelling/leakage, damage/corrosion, uncertain tool placement or
mechanical resistance, unexpected adhesive or layout, any need to disturb wiring,
or markings not visible in the permitted scope. Do not force a source procedure
to fit a different layout. A stop report with the reason is sufficient evidence;
continuing to meet a photo target is not required.

Keep original photographs private. For review/publication, crop or mask serials,
barcodes, account details and household background before sharing. Share only the
minimum geometry/revision evidence needed; no device identifier is required. No
raw source screenshots with visible unit labels are republished in the repository.

### Decision and follow-on gates

Before proceeding, the owner must review the scope, choose a competent operator
and explicitly authorize a specific inspection plan after the mechanical/safety
gaps are resolved. If that cannot be established, obtain a qualified repair
assessment rather than guess. No owner approval has been recorded for this plan.

After any separately approved identification, compare the actual board layout
before qualifying battery isolation or any UART/BootROM route. An interior photo
would not establish de-energization, pad voltage, storage backup, recoverable entry,
stock return or usable boot logs. Tasks #346–#348 and recovery phase #344 remain
open. Task #345 stays open until this proposal and its unresolved source limits
have been reviewed; no physical gate is closed by merging documentation.
