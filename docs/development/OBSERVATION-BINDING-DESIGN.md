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

## First implemented operation sequence: fake backend only

`offline_observation_adapter.py` now validates an injected backend's active
configuration/endpoint verdict, confirms interface claim, performs exactly the
three observation queries, then releases its confirmed claim and disposes the
backend. Command mapping is explicit input containing only those three names;
no real protocol constants, USB imports or backend implementation are supplied.
Every write must complete; an incorrect echo stops before a payload read.
Every transfer carries a positive timeout capped at500ms. Any failure produces
only an exception class, discards partial observation and performs cleanup.
A release/dispose failure also discards an otherwise complete result.

Three fake-backend tests verify the actual method trace and configuration, claim,
short-write, bad-echo, short-read and cleanup faults (228 full-suite tests pass).
No reset/configuration change/driver-detach method is available to this sequence.
Backend `validate_active` remains an injected trust boundary, not implemented USB
validation. A failed claim is assumed not acquired; a real backend must expose
uncertain ownership and dispose safely rather than claim guaranteed cleanup.

This is deliberately a partial implementation of the design: handshake and mode
exchange, actual endpoint/backend validation, total worker supervision and native
binding are absent. The5s collector budget is cooperative and cleanup calls are
not preempted here. There is no live CLI. Next integrate the owned supervisor
around this exact sequence using real stalled synthetic backend processes and
validate timeout/cleanup reporting before reviewing a native binding.

## Supervised adapter integration: actual synthetic processes

Run `python3 scripts/synthetic_supervised_observation.py --mode success`,
`--mode io-stall` and `--mode cleanup-stall`. This built-in-only CLI runs the
owned adapter in a spawned child with a1s parent deadline. The success output
is parent-validated against six owned source hashes; stalled write and stalled
release callbacks are real blocked synthetic processes, terminated/reaped and
rejected. Unlike the earlier fake-clock case, these exercise process supervision.
[Retained reports](../../evidence/supervised-observation/success.json) and sibling
fault reports record timings and hashes. Two integration tests bring the suite
to230; all three CLI cases were executed locally.

No external workers/native libraries/device inputs are accepted by this CLI.
This proves host handling of these synthetic stalls, not termination guarantees
for every native/OS state. In particular, killing a worker during interface
release does not establish actual device/interface cleanup or recovery. Output
remains unqualified and private temporary quarantine is removed after validation.
Next review the actual PyUSB backend binding implementation and its host-only
native-load dependencies; no physical enumeration is authorized by this package.

## Pinned PyUSB binding review: effects below the adapter

The cached PyUSB1.3.1 wheel and two reviewed modules were reverified against
[retained source identities](../../evidence/pyusb-binding-effects/source-review.json).
Source links: [core.py](https://github.com/pyusb/pyusb/blob/v1.3.1/usb/core.py)
and [libusb1 backend](https://github.com/pyusb/pyusb/blob/v1.3.1/usb/backend/libusb1.py).
This review imported neither package nor native library and enumerated nothing.

- Device.read/write call ResourceManager.setup_request, which resolves an endpoint
  and implicitly managed-claims its containing interface. Explicitly claiming one
  interface is insufficient if the later endpoint resolves to another. The binding
  must constrain both endpoint ownership and the interface actually used by IO.
- Endpoint resolution selects cached alternate settings, defaulting to zero.
  That cache is not a fresh device alternate-setting observation. Reject ambiguous
  alternatives; do not call set_interface_altsetting merely to make lookup work.
- get_active_configuration opens a handle and queries configuration on first use;
  it can subsequently return a cached configuration. A fresh owned device/worker
  avoids treating a previous session's cache as current evidence. Opening the
  handle is an effect even though this path does not call set_configuration.
- Device.read(size) returns an array, not bytes. The binding must make a bounded
  bytes conversion and validate the resulting length. Passing the array directly
  to our strict decoder correctly fails; loosening the decoder is unnecessary.
- dispose releases tracked interfaces but ignores some USBError release failures.
  Successful dispose therefore cannot alone certify confirmed release. Record
  explicit release success separately and preserve any failure even if dispose
  later returns normally. A closed handle is not proof of firmware recovery.

These findings prevent simply wrapping Device.read/write and returning True from
validate_active/dispose. Next implement a fake-PyUSB-tested wrapper with explicit
selected-interface/endpoint metadata, strict timeout/bytes handling and separate
release/dispose outcomes. Actual native handle acquisition, alternate-setting
verification and exact live endpoint ownership stay unqualified until reviewed.
No runtime dependency install or physical operation is needed for that work.

## Injected PyUSB-shaped wrapper implementation

`injected_pyusb_observation.py` now implements the backend methods against an
explicitly supplied device and utility object, importing no USB/native package.
It checks the active configuration's selected interface, rejects alternate
settings on that interface, requires globally unique selected bulk endpoint
addresses and bounded packet sizes, and claims only the explicit interface.
Read/write use only those endpoints with positive timeouts at most500ms and
64-byte bounds. Read arrays are length-checked then converted to bytes. Explicit
release failures remain sticky even if resource disposal later succeeds.

Four fake-object tests cover explicit IO/cleanup, ambiguous descriptors and
alternates, release failure, ownership/timeout and short-read faults;234 full-suite
tests pass. This is an implementation against the reviewed public API shape,
not a native runtime qualification. It does not discover/select devices, load a
backend, change configuration/alternate settings or detach drivers. The supplied
objects and fresh/exclusive device ownership remain caller trust boundaries.
No actual handle, interface, protocol command or tablet was accessed.

Next join this wrapper to the owned adapter in a fake-device integration test,
including uncertain claim/cleanup failures. Native-load ABI testing can then be
prepared separately without enumeration. Entry/handshake/mode and failure return
still require a concrete owner-reviewed route before physical use.

## Wrapper-to-adapter integration and uncertain claim ownership

Three integration tests now run `OfflineObservationAdapter` through the injected
wrapper and fake PyUSB-shaped device/utilities. Full synthetic replies arrive as
arrays and are converted/decoded; the actual trace uses only the selected OUT/IN
endpoint addresses. Short writes, mismatched echoes and short reads stop after
the first query and release/dispose the owned interface. Bad echoes cause no
payload read. These tests join the implementation layers rather than duplicating
their validators;237 tests pass in the full suite.

The integration exposed a cleanup reporting gap: if claim_interface raises after
an uncertain native operation, a later successful dispose cannot prove no claim
occurred. The wrapper now marks claim uncertainty before calling that operation,
clears it only on confirmed success, rejects retry and reports cleanup false
through disposal after a claim exception. No unconfirmed manual release is
attempted by the adapter. Explicit release failures likewise remain failures.
This preserves uncertainty; it cannot determine what a real OS/backend did.

Next prepare a host-only native ABI probe that loads only the pinned candidate
library and invokes no enumeration/context/device operations. Inspect the exact
initialization effects before executing that probe. This is a dependency check,
not device access or route qualification. Physical entry/handshake/return and
usable boot logs remain unqualified.

## Executed host-only native version probe

The exact staged arm64 candidate SHA256
`95c5d6ec5e955b5fb83253963805a0e25a6b1253e9c4e217eaad68e31bb04f4a`
loaded successfully on this Mac. Own `probe_libusb_version_only.py` verifies
regular-file length/hash, loads that absolute private path and invokes only
libusb_get_version with an explicit no-argument/four-uint16 result ABI. It reads
no string pointers. A10s parent subprocess bound was used; it completed normally.
[Retained output](../../evidence/libusb-version-probe/result.json) reports
1.0.30, nano12037. No context initialization, enumeration or device-open API was
called. No package/system install, relocation or security change was performed.

Pre-execution static inspection found no __mod_init_func section or LC_ROUTINES
command in this exact candidate, only its previously reviewed Apple dependencies.
This is bounded inspection, not a proof about all system dependency initialization.
The tagged [libusb implementation](https://github.com/libusb/libusb/blob/v1.0.30/libusb/core.c#L2922-L2930)
returns its constant version structure; it does not initialize the USB backend.
Library identity was verified against the staged bottle, while complete binary
reproducibility/signature validation remains outside this probe.

This resolves loadability and one narrow native ABI call. It does not qualify
PyUSB initialization (which may initialize a context), full API compatibility,
interface ownership, endpoint IO or tablet entry/recovery. Do not run backend
initialization merely as the next dependency check while the tablet-access ban
is in force. Next review PyUSB backend initialization to distinguish symbol setup
from context creation and device enumeration before any such execution.

## Context initialization is outside the no-enumeration probe

Pinned PyUSB1.3.1 [get_backend](https://github.com/pyusb/pyusb/blob/v1.3.1/usb/backend/libusb1.py#L961-L978)
loads symbols and constructs [_LibUSB](https://github.com/pyusb/pyusb/blob/v1.3.1/usb/backend/libusb1.py#L716-L733),
whose constructor calls libusb_init. It is not merely a symbol/load compatibility
check. The [libusb core](https://github.com/libusb/libusb/blob/v1.0.30/libusb/core.c#L2547-L2553)
then invokes platform initialization. The tagged
[Darwin initializer](https://github.com/libusb/libusb/blob/v1.0.30/libusb/os/darwin_usb.c#L850-L873)
returns through darwin_scan_devices. Thus normal PyUSB backend construction can
scan connected devices even without an explicit enumerate_devices call. It was
not executed. The successful version-only probe remains the current native limit.

The Darwin source also shows driver detach/attach can
[reenumerate the whole device](https://github.com/libusb/libusb/blob/v1.0.30/libusb/os/darwin_usb.c#L2649-L2720);
interface-scoped API names must not be mistaken for isolated interface effects.
The proposed wrapper omits these operations. A future supplied device must also
have independently established auto-detach policy; omitting explicit detach in
our wrapper alone cannot prove the native handle has it disabled.

[Review receipt](../../evidence/backend-init-boundary/report.json) records pinned
PyUSB identity and upstream tagged source links. No new runtime package, context
or device operation was performed. Next improve the wrapper's explicit injected
ownership contract to reject unreviewed auto-detach state and record that it is
an attestation, not a runtime getter. Continue source work on exact entry/return
options; native backend construction requires a separately authorized device
observation phase and cannot proceed during automatic no-access runs.

## Injected-handle caller prerequisites are now mandatory

The injected wrapper now refuses construction unless the caller explicitly
attests both disabled auto-detach and a fresh exclusively owned device object.
Omitted, false and merely truthy non-Boolean inputs are rejected before any
injected method call. Existing fake integrations explicitly satisfy their fake
object contract; a new test checks rejection without calls (238 total tests).

These inputs are caller attestations, not runtime inspection or authorization.
No native getter/handle factory is implemented, and no supplied object becomes
qualified merely by setting them True. A later live factory must establish and
record the facts rather than passing constants to bypass this contract. The
wrapper does not call a detach setter or acquire a handle to discover its state.
This closes the previously implicit caller-policy gap, not actual USB ownership.

Further native initialization would scan devices and remains outside automatic
runs. Next source task returns to current-stock entry/return alternatives: locate
an exact build-compatible starting state and a non-destructive failure exit.
Avoid expanding synthetic policy layers while those physical prerequisites are
unknown. The existing owner hardware-access preference remains pending.
