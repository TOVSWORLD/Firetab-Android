# Douglas minimal observation binding design

Status: design only. No live binding, entry procedure or tablet test is qualified.
This bounded task is to learn mode/version/security before selecting a read-back
agent. It does not load an agent, read storage, unlock or test a kernel. Parent106
and the [physical decision checklist](RECOVERY-DECISION-CHECKLIST.md) stay open.

## Implementation decision

Use an owned narrow adapter over a pinned PyUSB/libusb candidate, not MTKClient's
monolithic initializer. The source review identified fallback memory reads,
watchdog/identifier/authentication effects and unsupported-security defaults in
that initializer. Reuse our exact frame/session decoders as validators, not as
proof that transport is safe. Do not import upstream modules to get constants.
Document an independently authored protocol mapping with pinned source citations.

The candidate native library is statically inspected only. A native-load/ABI
check without enumeration would be a distinct later host task; no device
access is implied. No global package install, driver/security setting change or
new large download is required to write the adapter. Keep runtime files private.

## Fixed operation budget and device selection

A future worker must have a fixed reviewed operation plan, not an arbitrary
command shell. It should accept one owner-selected ephemeral device reference
from a separately reviewed inventory, not select the first matching vendor ID.
No serial number is needed in public output. Selecting by product ID alone cannot
prove the target is this tablet or its mode. Descriptor/interface/endpoint
validation must precede claims or protocol traffic; ambiguity aborts.

One attempt, no reconnect loop, no retries/fallback backend. Validate an already
active configuration; if unavailable or incompatible, stop rather than call
set_configuration. Claim only the reviewed interface. Do not detach/attach kernel
drivers automatically. A claim conflict aborts. Confirm endpoint direction/type,
packet extent and interface number before protocol IO. These choices may prevent
success on this host; failure is preferable to silent escalation of effects.

Initial handshake compatibility must be reviewed for the selected interface.
If CDC line coding or control-line requests are actually necessary, list their
exact effects in the owner test plan before enabling them. They are not assumed
necessary merely because the upstream helper sends them. No speculative control
requests, drain reads, memory/register reads or resets are included by default.

Every write must return the full requested length. Every read must have explicit
positive native timeout and exact-size validation. Proposed initial limits are
500ms per transfer and10s for the whole worker; they are engineering limits to
review, not measured device timings. The parent supervisor terminates/reaps the
owned worker after its budget; callback checks alone cannot stop blocked native
code. Worker termination is not firmware rollback or proof of USB cleanup.

## Permitted protocol scope

After a separately qualified entry and handshake, query fresh bootloader-mode
reply, hardware code, hardware version tuple and target configuration only.
Validate each reply/status immediately; any unsupported/short/unexpected response
ends the attempt. Do not turn unknown into disabled security or inferred mode.
The mode echo remains source-derived evidence pending actual qualification.
No unique identifiers are queried. No payload, agent, authentication, watchdog,
MMIO, memory access, storage read/write/erase, reset or reconnect is permitted by
this observation scope. Read-back bootstrap is a later reviewed procedure.

Implementation must account for distinct framing: bootloader mode is a direct
one-byte response; ordinary query commands require matching echo followed by
fixed payload. Our existing three-query orchestration does not yet perform this
mode exchange or establish its provenance. No current runnable CLI implements
this proposed live scope.

## Failure exit and restore boundary

On ordinary failure: discard partial results, release only the interface claimed
by this worker and dispose its resources without requesting device reset or
changing configuration/driver attachment. Cleanup failure is recorded separately;
it never converts a failed observation to success. On forced worker termination,
assume cleanup is uncertain. Do not immediately retry or force an entry transition.

This is a host failure exit, not a proven device recovery path. The owner plan
still needs an established way for this exact installed tablet to enter the
chosen protocol and return to normal stock operation after interrupted queries.
That must be qualified before execution. Do not intentionally corrupt preloader
or security state to manufacture entry. No escrow is collected or restore claim
made by this observation phase. Later payload/storage work still requires the
independent restore/logging gates in the decision checklist.

## Private evidence and public output

Private record: exact adapter/Python/PyUSB/native hashes, reviewed operation-plan
revision, sanitized topology description, phase timings, timeout/claim/release
outcomes, exact reply lengths and status categories. Keep raw transcripts out of
public artifacts until separately reviewed. No identifiers or host absolute paths
in public output; do not persist arbitrary exception strings that may contain them.

Public allowlist: source hashes; scenario/phase; elapsed time; success/error class;
reported hardware version words and SBC/SLA/DAA bits after explicit sanitization;
mode candidate with qualification false; cleanup outcome; no-device/physical
readiness flags. Do not include raw descriptor strings, serials, household data,
command buffers, authentication data or firmware bytes. Boot logs are a separate
capture path; observation protocol logging does not replace UART/persistent logs.

## Acceptance before any owner test

1. Implement this exact adapter behind a fake backend and prove its actual call
   trace contains only reviewed operations. Fail every partial read/write,
   claim/configuration ambiguity, timeout and cleanup edge; no fallback effects.
2. Pin independent protocol mappings and candidate native ABI. Verify no upstream
   helper import, implicit backend discovery or device access at module import.
3. Specify exact entry/return method for this stock build and owner hardware
   preference; the pending preference alone does not qualify an electrical route.
4. Produce an exact-hash package and one-attempt owner procedure listing effects,
   failure exit and sanitized evidence return. Ask for physical action only then.

Next implement the fake-backend-tested adapter operation sequence. Physical
execution remains outside automatic runs; no tablet action is requested now.
