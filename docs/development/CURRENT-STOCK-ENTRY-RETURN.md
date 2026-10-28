# Current-stock douglas: entry and return route review

Latest owner-session evidence: douglas identity and unprivileged sysfs partition
metadata are now observed. Original packages and named ranges are available;
raw GPT/security-state escrow, independent failure return and real boot logs
remain unqualified. See [observed layout](#owner-observed-partition-layout-347--346).


Reviewed2026-10-26. Target evidence remains build50.6.5.9_user_659664620,
PL7/LK3/TEE262; displayed Fire OS5.7.1.0 is not a substitute for those component
versions. No tablet was accessed and no helper was executed in this review.

## What the public USB-only guide actually establishes

The pinned [FireHD8-2017 guide](https://github.com/ryanfortner/FireHD8-2017/blob/91f93505eee47d6848dc6e161f29011503106a33/README.md)
reports the author's5.7.0.0/Linux setup. Its route uses intentional bricking,
then BootROM minimal and modified fastboot. It is not a read-only USB transition
or evidence of interrupted-query return on this exact build. The README's broad
recoverability reassurance is not an independently verified restore mechanism.
Its later bootloader/recovery success depends on completing the modifying chain.

The already inspected [sequence inventory](../../evidence/recovery-material/sequence-gates.json)
shows why the initial bootstrap and eventual recovery are separate: the minimal
path assumes prior changes and writes boot/security-related state, including
RPMB. A boot/user-region escrow cannot promise to restore that security state.
Current versus older official EMI identity resolves only memory-data provenance.
It does not make this sequence suitable for the first observation or backup.

## Remaining candidate routes and exact missing evidence

- **Stock recovery → stock fastboot:** potentially an observation starting point,
  not automatically BootROM or a RAM-loading capability. Exact current command
  acceptance, signature policy and normal-return behavior remain unknown. A
  guide reaching fastboot does not establish arbitrary boot support. No command
  was sent. A future test must distinguish OS reboot, USB reset, boot command,
  flash command and actual kernel handoff in its effect inventory.
- **Preloader protocol → BootROM:** the reviewed MTKClient candidate can invoke
  crash/reset/bootstrap behavior; that is not passive observation. Exact entry
  on this build and interrupted-attempt return are unverified. The owned minimal
  collector intentionally omits those transitions and cannot create reachability.
- **Hardware BootROM entry:** owner accepts hardware access if needed for planning;
  no traceable current
  board-specific point/electrical/entry-and-return procedure is qualified. Generic
  MediaTek advice or another Fire generation does not fill that gap. No opening,
  shorting, cable operation or measurement is requested.
- **Already modified recovery:** useful later, but not an established starting
  state on this stock tablet. An existing Android10 port does not prove the stock
  boot chain accepts the new diagnostic package without prerequisite changes.

The primary XDA page returned502 during this bounded refresh; the postmarketOS
page redirected to an inaccessible host. These access failures do not prove
missing methods or incompatibility. Search results were not promoted to verified
instructions. No full firmware/helper archive was downloaded.

## Direction and next source task

There is no newly verified non-destructive exact-build entry/return route from
this refresh. Keep106 open. Do not claim the host observation adapter has solved
entry merely because its synthetic tests and native version call pass.

Next inspect the cached current LK's stock fastboot handler inventory and boot
image verification path, recording source/disassembly identities and command
availability as static evidence only. Determine whether a RAM-only boot path
exists before planning a physical command. Do not publish raw firmware windows
or infer acceptance from command-name strings alone. A concrete owner test must
state what can change and how stock operation is restored after its failure.

## Exact stock LK registration-region result

Own `audit_stock_fastboot_registration.py` verifies cached current LK SHA256
`4ca0cca7ae9af6e959dc848b9ca002624c62e1bb93c83c0ecc89bae8d2186b08`,
then resolves Thumb literal/PC references and calls in the reviewed registration
region. Private llvm-objdump inspection of the common callee shows allocation
and linked-list insertion of label, length, flag and handler fields. This is
stronger evidence than string presence alone, but does not establish reachability
or permission under this tablet's actual security state.

The [metadata-only report](../../evidence/stock-fastboot-registration/report.json)
records13 label/call pairs and hashes of reviewed windows. They include getvar,
download, flash, erase, continue, reboot and OEM operations. No `boot` label was
resolved at these13 selected registrations. That is a bounded-region finding,
not proof that the complete binary has no alternate RAM-loading path. A separate
`boot` string reference appears elsewhere and may concern a partition rather
than a command; it is not accepted as RAM-boot evidence.

Raw firmware/disassembly stays under ignored out/. No physical command or
firmware was executed. Next trace the registration flag's dispatcher check and
resolve the continue/reboot handler identities; determine whether they merely
resume stock boot/reset and whether any path bypasses image verification. Keep
RAM-boot capability false until a complete accepted handoff path is established.

## Dispatcher and selected return-handler identities

Own exact-hash pointer audit resolves the registration table's continue, reboot
and reboot-bootloader handler pointers using the linked-address-base assumption
0x4bd00000. This is static pointer interpretation, not actual LK placement proof.
[Metadata-only report](../../evidence/stock-fastboot-handlers/report.json) retains
pointer-slot/handler offsets and hashes of privately disassembled windows.

The dispatcher first calls a separate command-prefix filter, before linked-list
matching and the indirect handler call. That filter uses static and dynamically
provided prefix lists. Its effective installed policy remains unknown; finding
an entry in the registration list cannot establish command permission. The
registration field at offset0xc is retained but its complete semantics are still
unresolved: this review does not label it an unlock bypass or security flag.

The resolved continue handler changes internal state, performs additional
calls whose effects remain unqualified and branches into another LK path; it is not evidence that the downloaded
RAM buffer becomes the kernel. Both reboot handlers reach a shared downstream
routine; reboot-bootloader invokes an additional setup call first. Their full
persistent/MMIO effects and successful normal-return behavior remain unqualified.
No command was sent, and no zero-side-effect recovery exit is established.

Next trace continue's downstream branch into the existing boot-image producer
analysis and the filter's dynamic-list producers. This will distinguish stock
boot continuation from any actual downloaded-image handoff without inferring
semantics solely from conventional command names. Raw disassembly stays private.

## Continue reaches the boot-labelled image producer

The exact-LK [continue path report](../../evidence/continue-image-path/report.json)
now ties the handler's zeroed global to the downstream mode selector. Private
control-flow review follows its mode-zero table entry through a short branch
into two calls with the `boot` label. The first call targets the same0x24770
image-header producer audited in [existing evidence](../../evidence/lk-header-producer/report.json);
that producer checks the Android boot-header structure. The second image-related
callee is0x24ce8; its complete verification/loading effects need further review.

This is concrete evidence that `continue` enters the boot-labelled producer
path, rather than evidence of direct handoff from the fastboot download buffer.
It does not establish all storage reads, final entry, signature acceptance or
normal return for the actual tablet. The linked global interpretation remains
under the same explicit static base assumption as the handler audit. No firmware
code or physical command was executed; only metadata and window digests are public.

Next inspect0x24770's image source and0x24ce8's verification/load boundary before
making a definitive claim about partition versus downloaded-buffer boot. The
filter's dynamic-policy producers remain separate unresolved work. Neither
`download` plus `continue` nor a conventional command name is a qualified test.

## Named-record and device-callback image origin

The [exact image-source report](../../evidence/stock-image-source/report.json)
now checks that both header producer0x24770 and image-loading callee0x24ce8
obtain an object from0x35da8 and resolve the supplied `boot` label through0x35c40.
The latter special-cases preloader names, otherwise searches20-byte named table
records and copies a matching record. Header reading shifts the record's first
word by9 before invoking the object's callback at offset0x10; the image callee
uses the same callback slot with offsets derived from that record/header.

This supports a named block/partition-style source rather than direct reuse of
the fastboot download buffer on the selected continue path. The callback's actual
backend implementation remains unresolved, so no observed eMMC read or complete
storage-origin proof is claimed. The table/provider can contain runtime state.
The image callee also invokes0x244c0 before further loading; its semantics and
later security-related calls require separate review. A header magic check is
not cryptographic verification, and a successful source lookup is not acceptance.

No physical command, memory read or firmware execution occurred. Next resolve
the callback provider's initialization and0x244c0's role, distinguishing header
validation, loading, signature policy and eventual kernel entry. Raw disassembly
stays private; public artifacts contain offsets, call identities and hashes only.

## Early check is range/size validation, not signature verification

Private exact-LK instruction review resolves0x244c0 as an arithmetic range/size
check. It rejects carry from unsigned start+length and a length strictly greater
than0x1000000 (16MiB), then applies further placement comparisons. Its caller
passes destination minus0x800 plus a runtime length global and rejects a nonzero
result. A diagnostic reference explicitly describes a kernel-size limit.
[Metadata/window-hash receipt](../../evidence/stock-image-range-check/report.json)
retains these findings without raw code or disassembly.

This removes a classification uncertainty: that early call is not cryptographic
signature verification. It also identifies a potential modern-kernel packaging
constraint on this stock path. The runtime length global's complete producer and
relationship to compressed kernel bytes, MTK prefix and image/header sizes still
need tracing. Do not label16MiB a universal hardware/RAM limit or assume it is
Android-version-specific. A differently implemented loader can have a different
contract. The complete placement predicate is not modeled or qualified here.

No patch, image repack or firmware execution was attempted. Next trace the length
global's assignments and the later actual integrity/security checks; compare
against exact diagnostic image sizes only when those bytes are available. Safe
placement, stock acceptance and recoverable first load remain unqualified.

## Resolved: 16MiB check covers a combined page-rounded extent

The header producer's assignment and the early check's input resolve to the same
linked global. Private arithmetic review shows, for normal non-overflow inputs,
`page_size * (ceil(kernel_size/page_size) + ceil(ramdisk_size/page_size) + 2)`.
Thus the previous diagnostic's wording is misleading if read as a kernel-only
budget: ramdisk and two extra pages also count on this selected path.

Own `audit_stock_checked_length.py` models only that reviewed arithmetic,
rejecting unsupported/overflow cases. It verifies exact LK and cached stock boot
hashes. The [stock result](../../evidence/stock-checked-length/report.json) uses
kernel7191666B, ramdisk1492335B and2048B pages, producing8689664B, below16MiB.
Two boundary tests distinguish combined extent from kernel-only size (240 tests).
No diagnostic image acceptance is inferred; other header fields, full placement,
cryptographic checks and any alternate producer paths remain outside this model.
Do not use overflow behavior to evade the limit or alter firmware checks.

Next investigate later integrity/security callees and the provider's backend
assignment. A diagnostic package using this stock path must satisfy the combined
extent constraint as well as all other unresolved loading/recovery requirements.

## Later verification result has a separate failure path

The [selected verification-boundary report](../../evidence/stock-verification-boundary/report.json)
now resolves the path after the size check and image callback. On one selector
branch, the loader invokes0x1cf0c. That wrapper forwards the image arguments into
0x1ce4c, then returns whether any bits in mask0x9 are set in its result. A zero
wrapper result reaches the explicit image-verification-failure diagnostic and
returns signed-13 from the image-loading function. This is distinct from header
magic checking and the earlier arithmetic range rejection.

The underlying routine calls0x1cf24 twice with differing first arguments; its
full result-bit meanings, key material and trusted-policy producers remain
unresolved. The selector at0x205ec can choose another branch at0x24f20, so this
selected trace is not a blanket proof that every installed mode enforces the same
signature policy. Nor is that alternate branch an established unsigned-image
route. Installed selector values, authorization and rollback semantics are not
known from static code alone.

No patch or bypass is proposed. Next identify the selector's input source and
result-bit/key-selection semantics, using metadata-only receipts. Keep actual
unsigned diagnostic acceptance false until the complete policy is understood
and a recoverable owner test is qualified. No firmware or tablet was executed.

## Selector input is an unlock-code record, not a fixed compile-time choice

The [exact selector-input receipt](../../evidence/stock-selector-input/report.json)
resolves0x205ec's field-name reference to `unlock_code`. It requests up to256B
through0x3a4, which dispatches a runtime callback and returns an error if that
callback is absent. A successful retrieval passes the buffer into0x2080c, a
wrapper around0x2062c's validation path. The selector converts the validator's
result into its branch decision. No input value or credential bytes were read.

This narrows the earlier alternate-path uncertainty: its selector depends on
retrieved and validated unlock-record state, rather than merely a command string
or host flag. The retrieval callback's installed backing store and the complete
validation algorithm/key selection remain unresolved. It is not evidence that
setting a record, choosing fastboot or sending an arbitrary code enables a path.
No such modification is proposed.

The underlying verification-result code also incorporates this selector into
additional result bits. The outer mask0x9 does not accept every nonzero status;
for example, bits0x10/0x20 alone do not satisfy it. Full result semantics still
need review before labelling success modes or trusted key slots. Next trace the
retrieval callback registration and validator's actual key/signature calls,
without exporting key material, credentials or raw firmware windows.

## Unlock record undergoes limited-unlock signature validation

The [exact validator-boundary receipt](../../evidence/unlock-validator-boundary/report.json)
resolves the diagnostic function label to Amazon's limited-unlock verifier. The
selected path requires a256-byte signature extent, calls a transformation whose
result must be256 bytes, and identifies transformation failure as RSA decryption
failure. A subsequent verification call must return exactly1 for its success
branch. These are checked call sites plus private instruction/diagnostic review,
not execution of the cryptography or a supplied credential.

This is stronger evidence that the alternate selector does not simply trust an
arbitrary nonempty unlock record. Full cryptographic algorithm parameters, key
origin, signed message, identifier binding and trusted-key selection remain
unresolved. No key bytes, unlock token, household/device identifier or raw firmware
window is published, and no credential generation or loader patch is attempted.
Do not describe this path as an available unlock service or authorized entry route.

Next resolve the record-retrieval callback's registration/backing-store path.
Keep bootloader entry, actual installed acceptance and recoverable return open;
learning a verifier's structure does not establish access to a valid token.

## Conditional callback registration resolves to a named-record reader

The [exact callback receipt](../../evidence/unlock-record-callback/report.json)
connects the getter's callback global to a conditional initialization assignment.
The assigned Thumb handler resolves to payload offset0xab4 under the existing
linked-base assumption. Private instruction review shows it validates a supplied
in-memory container, walks named variable-length records and copies the minimum
of requested and stored length from the matching record's data area. Missing
container/name/output cases have failure paths. No actual container was read.

This narrows retrieval from an opaque callback to an in-memory record lookup,
but does not yet identify the on-storage partition or source that populated that
container. The registration depends on an initialization branch; it is not
established that the observed tablet took that branch. Reported lookup success
also does not certify the stored record has the full requested length; subsequent
signature validation is a separate boundary. No stored credential or key material
is included in the public metadata.

Next trace the container's loader at0x3c370 and its initialization callers to
establish backing-store provenance. Keep this separate from device security-state
collection: no proposed observation command needs to retrieve unlock credentials.
No tablet access, firmware execution or persistent change occurred.

## Container loader reaches a selected block-read path

The [exact container-read receipt](../../evidence/record-container-read/report.json)
connects initialization to0x3c370, then0x3aefc. Its reviewed arguments specify
controller0, start block0, count30 and selector2. The wrapper invokes a selector
routine then a block-reading routine. The selector adjusts the low three bits
of a configuration byte through register index179 and reads back state. This
supports an eMMC hardware-region interpretation, but actual region identity and
contents have not been observed. The full controller/card setup remains separate.

A material limitation is that the wrapper does not branch on the selector's
return before issuing the read. Its final success/failure is based on the block
read's status. Therefore even this stock source trace cannot be used as proof
that an acquired container came from the intended region after selection fails.
Our independent escrow collector's acknowledged-region requirement still applies;
this is not a proposed method for collecting backups or credentials.

The loader normalizes wrapper failure, and initialization can fail before record
registration. No stored record, security key or per-device blob was extracted.
Next resolve controller/region mapping and the container validation identity from
primary source definitions, then assess what this adds to restore prerequisites.
Do not extend this into a device read or a write/selection helper execution.

## Primary-source region mapping and restore consequence

Linux v6.18 [MMC definitions](https://github.com/torvalds/linux/blob/v6.18/include/linux/mmc/mmc.h)
identify register179 as partition configuration, access mask7, first boot-area
access1 and RPMB access3. Its [boot-region creation](https://github.com/torvalds/linux/blob/v6.18/drivers/mmc/core/mmc.c#L425-L437)
uses first-boot access plus index for the two hardware boot regions. Combined
with the exact LK selector trace, access2 therefore identifies the intended
second boot hardware area, distinct from RPMB. This is a static inference, not
observed selection success; the unchecked selector-return limitation still holds.

Naming matters: this project's escrow `boot2` means the second hardware boot
region, typically Linux suffix `boot1`; Linux `boot0` is the first hardware boot
region. Do not map filename suffixes directly to protocol access values. The
[scope receipt](../../evidence/record-region-restore-scope/report.json) records
the interpretation. The selected container validator checks a static magic
reference; that tag alone neither authenticates contents nor establishes all
records/versions. No actual container was acquired.

Restore implication: a generic preloader/boot partition image or user-region GPT
backup does not cover this intended record store. Preserve both original full
hardware boot regions privately with independently qualified region identity
before any later change could affect them. Do not replace this area with another
tablet's image or publish its raw contents. This adds a concrete reason to the
existing escrow scope, not a restoration procedure or permission to read/write.
RPMB/key/counter/fuse recovery remains an additional unresolved requirement.

Next consolidate which proposed loading alternatives touch these areas versus
RAM only, using the already pinned helper/stock evidence; select the least invasive
plausible route with explicit entry and failure-return prerequisites. No further
credential analysis is needed merely to qualify original-state preservation.

## Selected stock reboot primitive (2026-10-27, #285)

The exact current LK's selected reboot and reboot-bootloader handlers both reach
the reset primitive at payload offset `0x28410` with argument one. The bootloader
variant additionally calls `0x288e8` first; that helper's complete state effects
are not yet resolved. The common primitive writes watchdog-related MMIO, calls
a wait helper, writes the final control register and enters a terminal self-loop.
The wait helper's units and actual reset completion are unverified. If hardware
does not reset as intended, this selected path does not simply return to caller.

The [metadata receipt](../../evidence/stock-reboot-primitive/report.json) retains
exact LK/window hashes, offsets and limits. Raw code/disassembly remains private.
The owned audit script checks exact binary identity before emitting this manual
review metadata. No firmware was executed and no fastboot command was issued.

This supports a stock reset-request path, not a qualified recovery procedure:
command reachability/filter acceptance, actual transition back to stock and
restoration of any changed state remain untested. Resetting cannot substitute
for restoring storage/security state or prove a RAM-only loading command exists.
Next resolve the bootloader variant's extra state helper and compare which route
can request stock return with the fewest additional effects, using static evidence.

## Bootloader-mode extra state and polling (#287)

The selected extra helper at payload `0x288e8` reads selector `0x802c`, sets bit
`0x2000` for argument one (clears it for zero), writes the result and invokes
`0x284e8`. The latter writes selector `0x803c`, then repeatedly reads selector
`0x8000` until bit `0x40` clears, with no iteration/time bound in that selected
loop. Read/write wrappers converge on shared backend `0x269c8`; its physical
identity and persistence semantics are not yet qualified. Access results are
not checked in these selected helpers. These are static decoded effects, not
an observed device transaction or proof of which state survives reset.

The [hash-gated metadata receipt](../../evidence/stock-bootloader-mode-state/report.json)
retains exact LK/window hashes and limits; private disassembly stays untracked.
Plain reboot's selected handler does not call this extra mode helper, whereas
reboot-bootloader does. Thus plain reboot is the narrower source-level return
candidate; neither command's current permissions or actual return is proven.
Reboot-bootloader adds mode-state and potentially unbounded wait dependencies,
so it must not be treated as a neutral equivalent of plain reboot.

Next identify the shared register backend and mode-flag consumption/clear path
from cached stock evidence, without commands or firmware execution. Initial
reachability, actual stock operation after failure, original-state restoration
and usable logs remain independent open gates.

## Conditional flag consumption/clear path (#289)

The exact-stock helper at `0x2892c` reads selector `0x802c` and extracts bit 13.
A selected caller at `0x243b2` tests that result; its nonzero branch at `0x24446`
stores mode code `0x63` and tailcalls the same setter at `0x288e8` with argument
zero, which requests clearing the flag. This establishes a static consume/clear
path, rather than leaving the flag's intended lifetime entirely unknown. It does
not demonstrate that the write succeeds, when the branch runs on this tablet or
which reset/power events retain the underlying state. Reader access status and
clear completion are not checked on these selected paths.

The shared backend's reviewed prefix uses MMIO, but its full hardware identity,
error/timing and persistence contract remain unresolved. The
[metadata receipt](../../evidence/stock-mode-flag-consumer/report.json) retains
exact LK/window hashes and offsets; raw disassembly remains private. No commands
or firmware ran. A requested clear is not restored original state, and mode code
alone is not proof of current command acceptance or an arbitrary RAM-loading path.

Next qualify the backend against cached platform source identity and distinguish
its hardware register channel from storage writes. Keep real entry/exit,
original-state restore and usable physical logs as separate untested gates.


## Hardware route planning accepted (2026-10-27, #291)

The owner explicitly accepts hardware access if needed. This resolves the route
preference, not board identification, a pad assignment, voltage, safe entry or
restore. No case opening, cable change, shorting, measurement or tablet command
is requested by this update. Automatic runs retain their no-device-access rule.

The existing UART source evidence supplies SoC GPIO79/80 function1 and UART0's
source register contract; it does not map those GPIO numbers to accessible PCB
pads. Before an owner procedure can be concrete, obtain traceable same-generation
board/revision evidence for pad geometry, ground/reference, voltage and routing,
and separate any BootROM-entry contact from UART transmit/receive. No pin or
contact should be inferred from another Fire generation or an unlabeled image.

A bounded primary-source refresh found the original douglas
[XDA thread](https://xdaforums.com/t/unlock-root-twrp-unbrick-fire-hd-8-2017-douglas.3962846/)
but retrieval again returned HTTP502. This is a source-access failure, not proof
that hardware entry is impossible. The pinned public GitHub guide already
reviewed remains an intentional-brick route, not board/electrical qualification.
No large download, helper or tablet operation occurred.

Next source task: locate revision-identifiable douglas board/UART evidence and
qualify its provenance before proposing any owner action. Continue independent
cached register-backend analysis if that source remains inaccessible. The pending
work is exact physical evidence, not another request for hardware-route preference.

## PMIC wrapper / RTC identity supported by cached source (#293)

The selected LK backend now strongly matches MT8163 PMIC-wrapper WACS2: its MMIO
base/command/status/clear locations and packed write/address/data encoding agree
with pinned cached platform source. That source's RTC definitions also match
all four selected mode details: selector `0x802c` is RTC_PDN1, bit13 FAST_BOOT;
`0x803c` is RTC_WRTGR; selector `0x8000` is RTC_BBPU with busy bit6. Thus the
extra reboot-bootloader state is supported as an RTC-domain fastboot flag through
the PMIC channel, rather than an eMMC partition write in this selected path.

The [receipt](../../evidence/stock-mode-pmic-rtc/report.json) links each primary
source at kernel revision `e0a3a2b2378ae4c7494ffdfea34d2a9e04a5fb74`, hashes
files verified against their committed Git objects and hashes the exact LK
window. Unrelated pre-existing source-checkout changes were left untouched.
This is cross-source alignment, not exact LK source/binary provenance. Actual
RTC retention across power/reset, write completion, flag clearing and original
state restoration remain untested. It does not prove a storage-free whole command
or authorize any register access.

A bounded board/UART primary-source search still supplied no revision-qualified
pad/electrical evidence; other-generation material was excluded. Hardware access
is acceptable for planning, but a board-specific procedure is not ready. Next
inspect RTC commit/error/retention source behavior and identify precisely what
an eventual owner-reviewed evidence collection would need, while keeping initial
entry, stock return, original-region restore and physical logs separate.

## RTC commit/error and restore boundary (#295)

Pinned cached RTC source strengthens the selected-LK interpretation: rtc_read
initializes data to zero and discards pwrap_read status; rtc_write returns no
pwrap_write status; rtc_write_trigger writes the trigger then polls CBUSY without
a local deadline. The MT6323 mode helper uses the same FAST_BOOT flag. Exact
primary source links, hashes and ranges are in the
[receipt](../../evidence/rtc-commit-error-boundary/report.json), verified against
committed Git objects. This is still source alignment, not exact LK provenance.

Inference: a lower-layer read error can be hidden as zero/clear, while a busy
value can keep the selected polling path waiting. A software return or observed
zero alone is therefore insufficient commit/clear evidence. Actual device error
behavior, power/reset retention and restoration have not been demonstrated.
Ordinary user/boot partition images do not by themselves prove RTC-domain state
restoration; that is a separate state artifact and reachable restore mechanism.
No RTC register was accessed and no helper/firmware executed.

Next source task: separate plain stock return from mode-changing entry and list
the exact original-state evidence each requires, minimizing additional state
changes. Keep RTC retention/restore, original partition restoration, initial
security and usable physical logs open rather than treating reset as rollback.

## OS ordinary versus named boot-mode restart source (#297)

Pinned cached `arch_reset` explicitly calls RTC markers for bootloader and
recovery command strings before its watchdog software-reset path. Its ordinary
unmatched-command branch sets the reset argument without calling those RTC
markers in the selected function. The
[receipt](../../evidence/os-reboot-state-effects/report.json) provides primary
links/ranges and source hashes verified against committed Git objects. This
supports the same least-additional-mode-state distinction as the LK handlers.
It is not proof that the running stock kernel uses these exact source bytes or
that the complete reset path changes no other state. Configuration gates and
successful watchdog API acquisition also matter.

Consequently, OS reboot-to-bootloader/recovery should be classified as named
mode-state operations, not equivalent to an ordinary restart or passive USB
observation. No reboot command was issued. A qualified owner plan would still
need actual mode/permission evidence, known original RTC state where relevant,
a reachable ordinary-return route and independent logs. Neither source branch
proves a bootloader accepts an unsigned diagnostic image or restores prior state.

Next consolidate the smallest separately reviewable mode/return evidence plan
for the hardware-acceptable route, using these effect distinctions. No physical
step is requested until the exact board/interface and failure exit are qualified.

## Original-thread correction and revised route priority (2026-10-27, #347)

The original discussion is readable in the browser even when the text-fetch tool
returns HTTP502. The [author's guide](https://xdaforums.com/posts/80154797/)
explicitly describes an initially case-closed route, partition changes and a
factory reset, with opening as a possible failure fallback. Its expanded section
contains a full-versus-minimal warning alongside older conflicting text; do not
flatten the whole page into one consistent command recipe.

The [maintainer correction](https://xdaforums.com/posts/90487831/) explains that
minimal mode skips components needed after the separate brick package. A later
[maintainer reply](https://xdaforums.com/posts/90490714/) recommends a native-Linux,
USB-first sequence for then-current firmware using the full stage. It rejects WSL
as the host for that procedure. These are primary-source route statements, not a
pass for our exact installed component versions.

Static inspection corroborates the distinction: the pinned mirror's full launcher
is 54 bytes and invokes main without the minimal argument. The already-cached
main guards the preloader/TZ/LK writes behind the non-minimal branch; common paths
still change boot/security state. Only 65,557 HTTP response bytes were used to
inspect the launcher within a 128KiB cap; no helper was imported or executed.
The [metadata receipt](../../evidence/douglas-original-route/report.json) preserves
hashes and source links, not copied helper code.

[Recent first-person reports](https://xdaforums.com/posts/90570763/) associate the
mirrored guide's brick/minimal pairing with boot loops. This is corroborating
failure evidence, not a controlled compatibility test. A reviewed
[5.7.1.0 post](https://xdaforums.com/posts/90777437/) asks about compatibility;
no successful exact-build reply was observed on that page. Do not turn unanswered
questions, broad version claims or a different unit's success into our test result.

### Decision for the next qualification work

USB-first is the primary candidate to qualify. Hardware inspection is fallback
preparation, not the sole prerequisite for discovering whether a route exists.
The [maintainer fallback](https://xdaforums.com/posts/90488396/) provides an
annotated board image and describes its mechanism, so the earlier source-access
block is resolved. Contacts must still match the actual board before any proposed
physical operation; this document prescribes none.

The owner reports an available Linux host; verify OS/tool versions and a direct
USB path without enumerating or accessing a tablet during automatic runs. Keep
its hostname/private access details out of public evidence. The other desk device
is a **Fire7 of unknown generation**, not another douglas; it is excluded from
this route. Record each future unit's model/generation/build separately.

Before an executable owner procedure: match original-author package metadata and
selected contents against the pinned mirror; audit the complete full-stage effect
inventory, including RPMB, GPT and erase operations; qualify original-state
coverage/failure return; then present exact host/device prerequisites, boundaries
and separate owner approval for destructive actions. No code changes to helpers,
no downgrade, flash, reset or connection is authorized by this source decision.
Task #347, restoration #346, logs #348 and parent #106 remain open. The revised
research priority no longer waits solely on the cover-photo review #345.

## Full-stage state transition and restore boundary (#347 / #346)

The full launcher is not a backup/observation phase. Hash-pinned cached main
source first transforms/writes both GPT copies when needed, then performs later
boot-region/RPMB checks. It clears a boot header and changes/rechecks RPMB state
in both modes. Full mode additionally replaces preloader copies, TEE and LK;
subsequent code injects boot/recovery payloads, requests a mode, restores headers
and reboots. The final fastboot script installs recovery, erases userdata and
changes MISC. These are separate mutation/failure boundaries, not one atomic
operation. The [selected-source inventory](../../evidence/douglas-original-route/full-stage-effects.json)
records exact ranges and source hash without redistributing helper code.

AST inspection found no call to the selected module's dump_binary helper in main.
This is not an exhaustive assertion about every imported helper, but no complete
pre-change region escrow is established by this selected path. GPT name reparse,
RPMB equality recheck and later recovery success are different evidence from
original-state readback/rollback. Do not claim this route preserves user data or
can restore all security state. A stock-return package is not an original backup.

The practical qualification choice must be explicit before execution: either a
separately qualified read-before-write/restore route, or an owner-approved test
unit and accepted irreversible-state/data-loss limits. That second option is a
change to the preservation requirement, not something automation can assume.
The Fire7 cannot stand in for a douglas test unit. First reconcile original
package identity and host preflight; then present the complete proposed effects
for review. No write, reset, wipe, helper or payload execution is approved here.

## Cached stock-return reachability audit (#346 / #347)

Static inspection of the cached chaosmaster/amonet Git revision
`2d8a4e6f73d9dab42d313c9cd751802b23ea7d31` identifies a separate dependency
from the full-stage loading path. Its return-to-stock script waits for ADB,
checks the product property, then obtains root before writing recovery or GPT.
It cannot be assumed reachable after loss of Android/ADB/root. The sourced root
fallback has an unbounded retry loop; it is not a qualified timeout/failure exit.
No helper was executed or imported. Exact hashes and ranges are in the
[source receipt](../../evidence/douglas-original-route/stock-return-source.json).

The script reads the current first 34 sectors and derives an unpatched GPT;
it does not acquire the original full user or both boot regions. It writes a
packaged recovery image, primary GPT and conditionally the generated backup GPT
using a local offset threshold. No post-write byte/hash readback appears in this
selected script. The imported GPT transformation was not audited in this scope.
There is no RPMB restoration in the selected script; this observation does not
claim exhaustive behavior of imported code or the unavailable original ZIP.

Its final reboot request is not proof that Amazon Recovery is reachable, that
an exact stock image is accepted, or that security state and user data return to
their original values. Therefore this script is an OS/root-dependent return
candidate, not the independent failure recovery required by #346. Next match
the original archive and audit its complete restore contents; separately resolve
a recovery path that survives the proposed failure. Keep both tasks open.

## GPT reconstruction is not original-sector restoration (#346)

The cached `modules/gpt.py` audit now closes the earlier selected-source gap
about how the return script derives GPT outputs. At pinned Git revision
`2d8a4e6f73d9dab42d313c9cd751802b23ea7d31`, it drops empty entries from the
parsed list and regenerates a protective MBR, fixed-format headers and a table
of 128 entries of 128 bytes. Original empty-slot positions and arbitrary original
MBR/header bytes are not preserved by that representation. CRC checks and
reparsing establish generated structure consistency, not pre-change byte identity.
Exact hash and ranges: [GPT source receipt](../../evidence/douglas-original-route/gpt-return-source.json).

The unpatch operation assumes userdata is third from the end of the compact
list, expands it to the header's last usable LBA, clears the last two entries,
and conditionally renames boot_x/recovery_x. It does not compare a separately
acquired original partition map. The generated backup offset derives from the
input header; source inspection does not confirm the actual unit's geometry.
These observations do not prove the intended supported layout fails, but they
exclude treating this tool as an arbitrary-layout original-sector restorer.

Acceptance remains either independently verified original-sector restoration
or an explicit owner-approved weaker return target and test-unit loss limits.
Neither has been demonstrated. A normal bounded GET of the published original
attachment also returned HTTP403 after the earlier browser failure; no archive
was saved. Original ZIP matching still requires accessible original attachments.
No helper code was imported, run or modified, and no tablet was accessed.

## Offline original-package intake (#347)

Once the three original files are supplied locally, run our owned inspector from
the repository root (v1.2, brick, return-to-stock order):

```sh
python3 scripts/inspect_recovery_originals.py \
  out/recovery-originals/amonet-douglas-v1.2.zip \
  out/recovery-originals/brick-douglas.zip \
  out/recovery-originals/amonet-douglas-return-to-stock.zip \
  --mirror-receipt out/recovery-provenance/extraction-report.json \
  > out/recovery-originals/intake-report.json
```

The inspector reads regular local files under the combined 31 MiB cap, hashes
whole archives, and decompresses only an explicit selected-content allowlist
under per-entry and aggregate caps. It rejects symlinks, encrypted entries,
unsafe paths and ambiguous selected names. It writes no extracted code, opens
no network/device and imports no archive module. It compares supplied bytes
with the optional own mirror receipt; equal bytes do not prove source custody,
archive authenticity, exact-build compatibility or recovery readiness. Missing
selected names are reported rather than silently treated as matches.

Keep the original ZIPs and report private in ignored output until provenance
and sanitization review. Supplied roles are positional labels, not authenticated
package identities. No real originals were available for this implementation;
synthetic ZIP tests establish host-tool behavior only. Original-author matching,
restore and physical-test readiness remain false even on successful inspection.

## Original-package review and owner decision boundary (#347 / #346)

**Disposition: package acquisition and selected identity comparison complete;
physical trial is not ready.** Normal Chrome attachment clicks retrieved the
three files from the original author post. The prominent legacy attachment.php
link returned404 and the automated download API timed out; neither failure meant
the canonical attachments were unavailable. The owner need not download them.
Actual combined size is31,461,609bytes, below the approved31MiB cap.
[The complete metadata receipt](../../evidence/douglas-original-route/original-package-review.json)
records source URLs, archive/entry hashes, component layout and inspection caps.
No archive code was imported or executed, and no payload was loaded.

All eight previously selected mirror entries match the originals byte-for-byte.
The original full launcher matches the separately inspected launcher, and the
original functions.inc, GPT tool and return-to-stock script match the cached Git
source audits. This resolves the original-versus-mirror selected-content question;
it does not authenticate an author signature or demonstrate this installed build.
All non-directory entries were streamed through SHA256/ZIP CRC verification under
128MiB per-entry and300MiB aggregate local decompression caps; none was extracted
for execution. Highly compressed brick images are about114MB each when decoded,
so compressed download size is not their device write extent.

### Effects and coverage presented for review

1. **Initial entry:** separate brick launchers send a packaged opaque brick image
   through bundled fastboot. Both then print minimal-stage guidance. The later
   [maintainer correction](https://xdaforums.com/posts/90490714/) requires the full
   stage for that separate-brick route. Do not follow the old bundled continuation
   in isolation or substitute a helper based on a similar filename. The opaque
   brick image's full device effects are not proved by its launcher command.
2. **BootROM bootstrap:** Python performs crypto/MMIO operations, disables caches
   and range checks, uploads a binary payload and transfers control. Static Python
   inspection is not proof of all native payload effects, RAM ownership or a
   bounded failure exit. No such sequence has run on this unit.
3. **Full storage stage:** conditional GPT writes precede later boot/RPMB checks;
   boot0 header changes and RPMB clearing are followed by preloader copies, tee1,
   LK, boot/recovery payload and MISC changes, header replacement and reboot.
   Final fastboot installs recovery_x, erases userdata and requests recovery.
   This is destructive and non-atomic. The rooted alternative also writes tee2;
   do not combine its effects or prerequisites with the selected full-stage path.
4. **Write-size limitation:** original main.py52–58 accepts max_size but passes
   zero to the lower write routine. Its partition-size arguments therefore do
   not enforce the advertised bound at this call. Exact padded component/write
   extents and actual partition geometry must be checked independently before
   any future execution; no upstream helper was patched. Original common.py's
   region switch method sends a selector without an acknowledgement check in
   that method. Neither observation proves an actual bad write occurred.
5. **Return package:** the original stock-return ZIP contains only a9,277,440-byte
   recovery image and the2,073-byte return script. It relies on the other archive's
   functions/GPT code, reachable ADB and root. It reconstructs GPT from current
   sectors and installs packaged recovery; it supplies no original preloader,
   LK, TEE, boot-region, userdata or RPMB backup/restore. It is not independent
   rescue after loss of Android/ADB/root.
6. **Recovery identity:** stock-return recovery and TWRP carry the same kernel
   component hash, which differs from the cached current-stock boot kernel.
   This does not identify an exact recovery build or prove incompatibility, but
   excludes calling it a hash-matched current-stock kernel. The recovery has
   2,048 trailing bytes unclassified by our header parser; no signature acceptance
   or exact firmware provenance is inferred from them. A compatible complete stock
   installation package and reachable installation mechanism remain prerequisites.

### Failure boundaries and acceptance remaining

Before any write, stop unless exact unit/build identity, package hashes, power,
host/session access, selected route, full effect inventory and independent log
capture/return are qualified. This review is a planning boundary, not an executable
operator procedure. After a possible persistent mutation, a timeout or disconnect
cannot be interpreted as no change: stop the session, preserve the host transcript,
and do not automatically retry another stage or run the stock-return script.
That script requires working dependencies the failure may have removed.

For preservation, either establish independently acquired original user/both boot
region escrow plus reachable compatible restore and explicit security-state limits,
or obtain a separate owner decision accepting a designated test unit's data/security
state loss and a weaker return target. The second choice still requires a credible
failure recovery/log route; consent alone does not validate the mechanism. There
is no existing complete original-state rollback for the described sequence.

Remaining acceptance is therefore concrete: exact current-build entry/failure exit,
complete binary/write extent and geometry review, reachable restore after the chosen
failure, and fresh attributable boot logs with retrieval. Hardware fallback remains
unit-specific and separately authorized. #346/#347/#348 stay open; no generic
compilation result, archive match or source review closes these physical gates.

## Original write extents and failure-return assessment (#347 / #346)

**Static slot arithmetic passes; actual target geometry and independent failure
return do not.** The owned `python3 scripts/audit_original_write_extents.py` checks
the hash-pinned original metadata against the selected source arithmetic. The
[write-extents receipt](../../evidence/douglas-original-route/write-extents.json)
is reproducible without importing helpers or reading a device.

The helper assumes512-byte sectors and pads whole files to that boundary. Its
preloader headers occupy bytes0–4096; the two preloader copies occupy byte ranges
4096–143360 and266240–405504 (ends exclusive). These four component ranges do
not overlap. New boot/recovery slots are each115,343,360bytes by the GPT tool's
0x37000-sector declaration. Each slot's4,096-byte header and492,544-byte padded
payload at sector223223 fit that declared slot, leaving560,640bytes at its end.
This proves only the selected declared profile, not an already modified GPT.

TEE requires3,307,008bytes; LK requires486,400 padded bytes; TWRP requires
13,512,704bytes in their respective target partitions. Generated primary and
backup GPT outputs are17,408 and16,896bytes. Absolute user-region LBAs, actual
partition capacities and valid backup placement remain unavailable from these
sizes alone. The two brick image lengths are not a description of their full
persistent effects or ordinary partition write extents.

Previously authorized cached `/proc/partitions` has selected kernel-reported
internal block-node sizes, now retained in a [sanitized receipt](../../evidence/douglas-original-route/cached-block-sizes.json).
It reports user capacity15,758,000,128bytes, boot0 node1,048,576bytes and boot1
node4,194,304bytes. The declared preloader extents fit the reported boot0 node,
but unequal kernel boot-node sizes must not be silently normalized into physical
EXT_CSD geometry. The cached report contains no raw GPT, GPT-name/start mapping
or EXT_CSD. Therefore it cannot establish tee1/LK/recovery_x targets, actual
region selection, protected extents or a complete original-state backup.

The cached candidate native source clarifies the selector limitation: its command
handler prints the mmc_set_part return value and delays, but sends no framed
acknowledgement to the Python host for that command. The [native source receipt](../../evidence/douglas-original-route/native-selector-review.json)
pins exact files/ranges. Shipped binary-to-source equivalence is not established;
this is a candidate protocol explanation, not proof of deployed behavior or a
validated selector. Header/MBR plausibility reads are not independent region
identity evidence. No native build or helper execution occurred.

### Which failure boundaries have an independent return?

- **Before any device mutation:** stopping host preparation needs no recovery.
  This is the only boundary with no assumed on-device change.
- **After separate brick or intentional header clearing:** USB BootROM re-entry
  is the proposed mechanism; exact current-build entry and persistence through
  the intended failure are unobserved. If it fails, the hardware fallback needs
  unit-specific board/contact qualification and separate owner action. Neither
  is a demonstrated failure exit today.
- **After GPT/component/RPMB changes:** entry to BootROM alone is insufficient.
  Restoring original state also requires correct region identity, original data
  and a compatible writer. Original region escrow is absent and ordinary images
  do not undo arbitrary RPMB/security-state changes. No qualified rollback exists.
- **After preloader headers are restored/reboot requested:** the earlier cleared-
  header mechanism no longer guarantees BootROM re-entry. Modified fastboot/TWRP
  may be the intended forward state, but neither has been observed on this unit.
  The original ADB/root-dependent stock-return script is not an independent rescue.

The next useful evidence is exact target geometry/selection and a concrete,
reachable failure exit with attributable logs. Acquiring it may require separately
approved device activity; none is requested by these offline commands. This
review does not authorize a trial, relax preservation requirements or substitute
a Fire7/other revision for douglas. Tasks346/347/348 remain open.

## Minimal next layout-evidence request (#347)

Cached MediaTek source provides a narrower metadata route than raw GPT or root:
`/proc/partinfo`. The source registers a mode0444 read-only proc file, selects
mmcblk0 and prints partition volume names, start offsets and sizes in hexadecimal
**bytes** (sector values multiplied by512). This could supply the missing named
partition ranges. Exact hashes/ranges and conditional build gates are in the
[partinfo source receipt](../../evidence/douglas-original-route/partinfo-source.json).
Actual installed presence, source match and shell/SELinux permission are untested.

The existing owner-run `collect_stock_facts.py` now requests this one extra proc
file through its bounded read-only reader after the douglas identity gate. No
collector was run on a tablet during this change. If the file is missing, denied,
truncated or timed out, collection records it unavailable; do not retry with root
or read a block device. The read-only collection scope does not authorize other
helpers, reboot, firmware modification or service changes.

For a separately approved targeted owner read, the concrete request is:

```sh
adb -s YOUR_LOCAL_DOUGLAS_SERIAL shell cat /proc/partinfo > partinfo-private.txt
```

The selector stays private/local and must identify the already known douglas,
not a Fire7 or another unit. Do not post the command with a real serial. Inspect
and sanitize the output before sharing; a denial/missing-file result is useful
and must not trigger privilege escalation. This command is presented for review,
not executed or authorized by this document or an automatic heartbeat.

Do not interpret the tool's pgpt/sgpt rows as verified raw GPT geometry: source
synthesizes512KiB entries, and sgpt starts at the end of the last iterated
partition. Even successful named metadata would not prove GPT CRCs, backup-header
placement, EXT_CSD, acknowledged selection, original-region escrow or failure
return. It would narrow the write-capacity question only.

## Owner-observed partition layout (#347 / #346)

After owner-installed host USB permissions and owner acceptance of the ADB host,
identity reads confirmed Amazon/KFDOWI/douglas. `/proc/partinfo` is missing on the
installed build; its source presence was not a runtime guarantee. An equivalent
unprivileged sysfs metadata read returned start, size and partition-name fields
for all16 internal mmcblk0 partitions. No root, block-device reads, reboot,
helper or firmware execution occurred. Raw host/device selectors remain private.
[Sanitized observed metadata and comparisons](../../evidence/douglas-original-route/observed-partitions.json)
retain the capture hash, units and explicit limitations.

The16 named ranges are nonoverlapping; boot/recovery and userdata names are
present, while boot_x/recovery_x are absent. Existing boot is16MiB, recovery17MiB,
LK512KiB and each TEE5MiB. Original LK and TEE components fit these reported
capacities. TWRP fits the reported recovery capacity with4,313,088bytes slack;
packaged stock-return recovery fits with8,548,352bytes slack. These are size
comparisons, not image acceptance or a statement that writing them is safe.

The exploit header/payload layout at sector223223 does **not** fit either
existing boot or recovery partition. It relies on the helper's GPT transformation
creating two115,343,360-byte slots and renaming the original partitions. Applying
only that reviewed arithmetic to the observed userdata end projects a231,194,112-
byte userdata shrink, including alignment loss. The projection is not an executed
partition change or proof that actual GPT headers satisfy the helper assumptions.
Do not apply the large-offset writes directly to the original partitions.

This resolves kernel-reported names, starts and capacities for the observed unit.
It does not establish raw GPT CRCs/header copies, original region escrow, native
selector acknowledgement, security-state restore, image acceptance or a failure
return. No modified fastboot/TWRP/BootROM path or boot-log lifecycle was tested.
The next gate is an independent, reachable recovery/log route with explicit
preservation limits; no destructive trial is authorized by successful ADB access.
The source-only proc request is superseded by this successful sysfs observation;
there is no remaining USB permission or owner file-supply blocker.

## Observed restore/log access disposition (#346 / #348)

The follow-up owner session refreshed current build/PL/LK/TEE and checked only
metadata permissions, current kernel-log access and a kernel-tag-filtered archive
query. Ordinary shell access has not established original-region escrow or usable
boot logs. Direct kernel access is denied, the protected copied log was not read,
and the diagnostic archive reports no SYSTEM_LAST_KMSG entries. See the
[observed access review](RECOVERY-AND-LOG-QUALIFICATION.md#owner-observed-restore-and-log-access-346--348).
No raw storage acquisition, root, reboot or firmware/helper execution occurred.

The owner has now accepted a wiped douglas test unit for planning. Next qualify
a concrete supported-stock return and failure-log mechanism for that target. Accepting a wiped test unit
is not permission to execute or proof the route works. Existing automatic-run
prohibitions remain in force even while ADB is connected.

## Current owner-selected recovery target

The owner accepts wiping this douglas and bootloader/security-state changes for
planning. Exact original data/security-state preservation is no longer required
for this unit; historical original-escrow gates are not the current blocking
acceptance target. No flash/helper execution is approved by that decision.
Supported-stock return after the intended failure and independent logs remain
required. [The observed access and exact-build installer review](RECOVERY-AND-LOG-QUALIFICATION.md#selected-wiped-test-unit-return-target)
defines the candidate full OTA and remaining authentication/access/resource gates.

## Full stock artifact now available

The owner-approved907,705,758-byte exact-build stock OTA is downloaded and its
whole-file SHA256 and RSA/SHA1 CMS signature verified. Its signer key material
matches the original bundled stock-return recovery's key file. The earlier
large-download blocker is resolved; see the [verification and trust limits](RECOVERY-AND-LOG-QUALIFICATION.md#approved-full-stock-candidate-hash-and-signature-346).
This does not establish deployed recovery trust, actual sideload/update acceptance,
rollback behavior, failure return or real logs. No firmware was run or installed.

## Stock recovery update-chain gap narrowed

The exact-build OTA's signed system data includes the recovery-install script,
IMGDIFF2 patch and bonus resource. Packaged boot init declares its oneshot service;
script input/target hashes agree with the signed boot/recovery manifest. See the
[static reconstruction-chain review](RECOVERY-AND-LOG-QUALIFICATION.md#exact-build-recovery-reconstruction-chain-found-346).
This explains the absence of a direct recovery write from the selected OTA script.
No patch/helper was executed and no successful boot-time reconstruction or
post-failure rescue is inferred. The earlier unknown asset/source location is
resolved; actual recovery reachability and failure logging remain separate gates.

## Exact current recovery artifact is available

Owned offline decoding now produces the9,299,968-byte recovery whose hash matches
the signed current-build OTA target. It also matches the stock boot kernel
component and fits the observed recovery partition. See the [decoder, controls and
runtime limits](RECOVERY-AND-LOG-QUALIFICATION.md#exact-stock-recovery-bytes-reconstructed-offline-346).
This replaces the older bundled recovery as the exact-build artifact candidate;
it does not establish bootloader acceptance, actual recovery boot or failure return.
No patching helper or image was executed, and no tablet was accessed.
