# Timeout and checksum source review

Pinned helper UsbClass.usbread initializes timeout=0 at530 and passes that value
as the second positional argument to endpoint.read in its fast branch at560.
The counter changes only after timeout errors; it is not an absolute deadline.
Static inspection of the hash-verified PyUSB1.3.1 wheel confirms Endpoint.read
forwards the explicit timeout and Device.__get_timeout preserves zero. Its libusb
backend forwards that value to the bulk transfer API. The [official libusb API](https://libusb.sourceforge.io/api-1.0/group__libusb__syncio.html)
defines zero as unlimited. Therefore the selected fast path can begin with an
unlimited blocking call. This is a source-verified conditional path, not an
observed hang on this tablet. No backend, library or helper was executed.

Only the previously measured58465-byte PyUSB wheel was fetched to read two ZIP
source entries. Its exact advertised SHA256 matched; package source stayed
ignored and was never imported/installed. Other planned Python wheels remain
undownloaded. Receipts/source hashes and helper line references are retained.

The legacy reader consumes/logs a two-byte checksum, but no read-checksum
algorithm or comparison is established by that code. A writer branch computes
an additive checksum; that alone does not prove the read protocol uses the same
algorithm. Do not invent a verifier from the field width. Host SHA256, exact
length and repeated reads do not by themselves certify a protocol checksum.

Our callback-only OfflineDeadlineReader now enforces exact logical read lengths,
positive bounded timeout arguments and a monotonic overall read budget. It
accumulates nonempty partial packets and preserves extra packet bytes for the
next logical read. Empty/invalid/oversized packets, transport exceptions and late
results fail, erase buffered tail and permanently invalidate that reader instance.
It does not retry or claim an unsynchronized stream has recovered.

Four tests use own fake clocks/packet callbacks: exact/tail behavior, shrinking
positive timeouts, late return, partial/empty/error responses and bad budgets.
No USB/native calls occur. Run
`python3 -m unittest discover -s tests -p test_deadline_reader.py -v`.

A callback must honor its positive timeout. This Python code **cannot preempt a
broken/blocking native call**; its late-result check runs only after control
returns. Millisecond rounding can add less than one millisecond to a native
request. Physical transport integration, actual timeout compliance, reconnect,
checksum validation and device state after failure remain unqualified. No
replacement upstream method or live acquisition binding was activated.

Next add a host-process deadline supervision contract tested with synthetic
workers so a native stall cannot trap the controlling process. Killing a host
worker will not prove device recovery or undo firmware side effects; those gates
must remain open. Any future worker's output stays quarantined until validated.
