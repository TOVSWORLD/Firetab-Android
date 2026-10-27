# Current-stock douglas: entry and return route review

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
- **Hardware BootROM entry:** owner preference is pending; no traceable current
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
