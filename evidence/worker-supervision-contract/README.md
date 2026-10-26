# Owned host-worker deadline contract

This own supervisor has no device/helper binding or command-line launcher. It
spawns a supplied trusted Python worker with a private quarantine directory,
waits at most the explicit deadline (maximum30s), then terminates and, if needed,
kills **only that owned worker** with bounded grace periods. No process-name
search, device reset or USB operation is implemented.

Parent acceptance requires timely worker exit0, a fixed completion message and
successful parent validation. Partial/failed/timed-out outputs are not validated
or published. Successful output remains quarantined for further review; there
is no automatic backup publication. Child status uses fixed small byte messages,
not untrusted pickle payloads or raw exception text. Worker stdout/stderr are
discarded in this prototype, including its OS descriptors; this is not a usable
physical boot-log capture path. A future live worker needs a separately qualified
private bounded logging design before use.

Tests execute real **synthetic** spawned child processes: completed fake output,
worker exception, validator rejection and a deliberately stalled worker that
ignores SIGTERM. The latter is killed/reaped and its partial output removed.
No firmware/helper/native USB code, backend or tablet is involved. The focused
four-test run passed in1.499s locally; the full199-test suite passes. Run
`python3 -m unittest discover -s tests -p test_worker_supervision.py -v`.

This is not an OS sandbox or proof that a native driver can always be killed.
Trusted workers must obey the staging-directory contract and not spawn external
process trees. Parent validation is a separate trusted/bounded callback, outside
the worker execution deadline. Scheduling/process-start/termination add overhead;
the contract is not a real-time guarantee. If the OS does not reap the worker,
its output remains quarantined and unaccepted. Concurrent hostile filesystem
changes and worker side effects outside quarantine are not contained here.

Killing a host process does not undo device writes, unload a RAM agent from the
tablet or establish return-to-stock recovery. Native timeout behavior, bootstrap
side effects, protocol checksum, safe entry/restore and usable logs remain open
under106. The original helper and staged libraries remain unexecuted. No Python
packages, global loader/security settings or tablet state changed.

Next assemble the already tested host contracts into one synthetic-only session
proof, explicitly excluding bootstrap and live native/device callbacks. Require
all component digests/review states and leave runtime/device readiness false.
Do not turn individual unit-test success into an owner-operated package claim.
