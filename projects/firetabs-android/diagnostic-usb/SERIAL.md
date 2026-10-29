# Bounded ACM status output source

Updates #27. The separate PID1 now maps its admitted emit callback to actual
serial syscall adapters for one fixed allowlisted status frame. **Current seven
admission gates remain zero; no runtime mount, node, TTY or gadget action is
admitted.** No physical descriptors are assigned. Default archive compilation
may optimize the unreachable admitted path away; actual admitted C paths execute
only under RAM-backed native tests, and also compile as AArch64 objects.

The callback reads the owned ACM function's read-only `port_num`, constructs the
matching ttyGS class path and reads its dynamically assigned major/minor. It does
not assume port zero, a static device number or mount devtmpfs. Decimal parsing
requires exact newline-terminated bounded values. A private0600 character node at
`/dev/firetabs-acm` is created once; existing nodes are rejected. Open uses
O_NOFOLLOW/O_NOCTTY/O_CLOEXEC/O_NONBLOCK. statx AT_EMPTY_PATH verifies the opened
fd's character type and expected dynamic identity before TTY ioctls. The owned
function port is rechecked. These checks supplement the separately unqualified
immutable-namespace gate; they do not solve concurrent privileged mutation.

TCGETS snapshots the prior settings. A non-N_TTY discipline is rejected without
changing it. TCSETS requests raw input/output/local flags,9600/8-bit/CREAD/CLOCAL,
no parity/stop/flow/hangup flags, VMIN1 and VTIME0, then requires exact readback.
Original settings are restored on every attempted raw-setting path, including
failed TCSETS. Cleanup closes once without retry and unlinks only the private
owned node. Primary output errors survive restoration/close/unlink failures;
retained ownership/error fields are explicit. PID1 then performs its existing
unbind-first gadget cleanup. A stale node from failed unlink is not adopted by
another attempt. No shell, ADB, storage, input read/command parser or console-over-
USB feature is added. SELinux permission/policy requirements remain unresolved.

The only serial payload is the fixed frame in acm_serial.h. It contains no
cmdline, UDC name, device numbers, serial identifier or raw boot log. Writes advance
only by actual accepted bytes, retry EINTR within128 total attempts and sleep10ms
on EAGAIN, also within that budget. Short/zero/oversized/error returns, failed sleep
and exhausted budgets fail explicitly. This bounds userspace attempts, **not wall
clock duration**: the pinned u_serial close path can wait15*HZ for queued output and
then discard remaining bytes. RAM tests cannot qualify driver/MMIO latency.

A successful write means kernel acceptance, not host receipt. Pinned gs_write
queues into a FIFO even without a connected USB port; acm_set_alt ignores the
called gserial_connect return. Close/queue drain can discard bytes. The frame
therefore says HOST_RECEIPT=unverified; no transport or retained-log gate passes.
Physical role/analog/clocks/loading/independent return/policy remain unqualified.

Evidence pins f_acm/u_serial and exact termios/stat/device-number headers, including
ARM64 directory absence of ABI overrides. Actual pinned UAPI structs compile in
layout controls for36-byte termios and256-byte statx with rdev offsets128/132;
modern kernel new_encode_dev is used, not the legacy8-bit UAPI MKDEV macro.
Source/constant/hash drift controls run via validate_usb_acm_serial.py. Actual C
RAM tests use allocated port2 and dynamic major273/minor1025, cover23 failure
families, partial/EINTR/EAGAIN output and cleanup, raw readback and ioctl retries.
ASan/UBSan and warnings-as-errors remain enabled. GNU AArch64 object/static archive
proof and separate exact-head Clang CI are compilation only, never device execution.

Next: host-side bounded capture/frame validation and private receipts with mocked
read/timeouts, then explicit physical admission dependencies. No host-received
status, full boot-log export or failed-boot retention is claimed by this scope.
