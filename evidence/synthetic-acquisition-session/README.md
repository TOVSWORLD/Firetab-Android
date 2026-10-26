# Synthetic-only acquisition session integration

This runnable host self-test joins the own packet deadline, memory-read binding,
exact host capture, worker supervisor and offline hash/GPT verifier. It accepts
only three built-in fixture modes; there is no arbitrary worker/module/device,
bootstrap, native-library or transport input. No upstream helper code is used.
A shared fixture builder generates a small GPT image and two ordinary byte
patterns; these are not firmware, tablet dumps or a real protocol simulation.

The worker captures all three synthetic regions through explicit geometry and
read kwargs, packet callbacks and private host files. Parent validation checks
source/component/reference metadata identities, expected lengths/SHA256 and both
GPT locations before accepting the host session. Successful data remains in a
private quarantine, never published as a real backup. Fault modes inject short
data and a blocked packet callback; the latter requires the parent process
supervisor, since a soft read deadline cannot interrupt that callback.

Run on a host with the repository's standard Python/test dependencies only:

- `python3 scripts/synthetic_acquisition_session.py --output out/FRESH_SUCCESS`
- `python3 scripts/synthetic_acquisition_session.py --output out/FRESH_SHORT --mode short`
- `python3 scripts/synthetic_acquisition_session.py --output out/FRESH_STALL --mode stall --timeout-seconds 1`

Output directories must be new and inside ignored out/. Each run uses73728
fixture bytes, at most5seconds default worker budget (explicit maximum30s),
small host memory/temp files, no downloads/install or paid resources. The host
capture component also checks its64MiB free-disk margin. The program does not
open or enumerate USB and can run independently of the tablet.

scenario_passed means the named synthetic scenario behaved as expected. For
short/stall it means rejection, not successful capture. host_session_accepted
is separate. Component and reference-metadata SHA256s, source commit/dirty state,
expected/validated region hashes and worker outcomes are retained. References to
the real candidate library/helper review are JSON metadata only; those private
source/binary files are never opened or executed by this integration.

Tests confirm the full generated session, short-response rejection and stalled
callback cleanup, with no completed region files retained after faults. Existing
standalone component fault tests remain separate. This does not prove the real
DA protocol/checksum, actual helper/native binding, bootstrap side effects,
physical entry/restore or usable UART/USB logs. All live/readiness flags stay
false. It is a host integration self-test, not a tablet diagnostic package.

Next checkpoint is choosing the physical-route constraint (USB-only versus
owner-performed hardware access) while independent source work continues. No
opening, connection, reboot, unlock or flash is requested by this self-test.
