# Private host status capture

Updates #27. `scripts/capture_usb_acm_status.py` promotes the tested callback-only
receiver into actual POSIX file/read adapters and an explicit CLI. It does not
activate a gadget, load an image, discover ports, issue ADB commands, change a
USB mode or configure host termios. Current serial device capture admission is
**false**, independent of the seven denied PID1 gates. The explicit serial flag
alone cannot enable it; a profile enabling serial/runtime qualification is rejected.
Serial adapters are tested only with mocked OS calls, never a device endpoint.

The frame and whole producer-header SHA are locked by host-profile.json. Header,
frame, length or admission drift fails before input/output opens. The receiver
core is the existing prototype, with injected read/monotonic/pause callbacks and
its original split/deadline/error controls retained. It permits exactly one fixed
73-byte status frame, no prefix/extra bytes in returned chunks and no CRLF rewrite.
A complete read returning after its deadline fails. Attempts/bytes are bounded;
this does not preempt a kernel or filesystem call that stalls. No endpoint-silence
or subsequent-stream claim follows from accepting one frame.

A source-only offline example is:

```
python3 scripts/capture_usb_acm_status.py --input-file out/private-fixture --output out/new-capture
```

Both paths must be direct children of the workspace's ignored out directory;
the output directory must be new. Inputs/selectors must be owned regular0600
single-link files, not symlinks. Offline input is at most74 bytes; full file size
and stable metadata must agree with the accepted frame, so a short read cannot
hide trailing fixture data. A validated offline fixture is never a host/device
observation. Existing outputs are rejected without adopting/deleting their contents.
The tool creates output0700, raw.bin0600 and private-receipt.json0600 with exclusive,
no-follow opens. Directory fds anchor operations. Partial writes/EINTR and write
budgets are checked; output EAGAIN is an artifact failure, not an input retry.

Raw bytes, selector paths, endpoint identity and invalid-capture hashes stay
private. Stdout is a bounded normalized JSON result; parse/I/O errors never echo
arguments, exception text or raw data. Valid-frame hashes are public constants.
Malformed/timeout/raw-write failures retain only bounded private raw evidence.
Incomplete receipt cleanup checks the owned inode before deletion and preserves
unrelated replacement files. Primary read/validation errors survive close/sync/
receipt errors. Close is never retried. The private receipt records its stage
before final directory descriptor teardown and explicitly says that teardown is
pending; stdout is the final result and reports any teardown error as failure.
No receipt or successful artifact implies boot/runtime qualification.

The serial branch, currently denied before selector or device opens, accepts only
an explicit private selector containing one allowlisted /dev/ttyACM* or macOS
/dev/cu.usbmodem* path. The isolated adapter opens read-only/nonblocking/no-ctty/
no-follow/close-on-exec and requires a character TTY. Read-only tcgetattr verifies
already-qualified raw9600/8-bit/CREAD/CLOCAL/no-flow/no-hangup settings. It never
sets them. This check and open flags do not qualify control-line side effects or
hardware behavior; source admission stays denied. No option overrides it.

Validation: native filesystem/CLI tests under temporary private directories plus
mocked serial descriptors, all receiver split points, deadlines/EINTR/EAGAIN,
short/write budgets, source drift, permissions/links/metadata, sync/close errors,
receipt ownership and stdout privacy. The actual offline CLI receipt in
 evidence/usb-acm-host/offline-cli-result.json explicitly records offline-fixture,
 host_frame_observed=false and runtime_qualified=false. No raw capture is published.
Prior PR423 exact Clang receipt is normalized in
 evidence/usb-acm-serial/clang-build-result.json; denied artifact hashes unchanged.

This captures only the fixed status frame, not arbitrary boot logs or failed-boot
retention. Physical loading/role/analog/clocks/enforcing policy/namespace/descriptor
assignment and independent failed-load return remain unqualified. Next independent
existing #27/#18 source scope is the unmatched AUDSYS provider contract and actual
child ownership/build prerequisites, with decoded-node controls and all unrelated
failed diagnostics preserved. #340 beta packaging remains blocked on actual gates.
