# Candidate entry transitions: source boundary

This independent source review continues while the owner's hardware-access
preference is pending. It does not assume USB-only is impossible or that case
opening is mandatory. No helper, native backend, USB or tablet was accessed.
The syntax-only reproducer is `python3 scripts/audit_entry_transition_sources.py`;
all five cached module hashes must match the pinned public import inventory.
No arguments containing register addresses or payload bytes are published.

At MTKClient7cb40e727727dfe3faa065eefb29b16ed29bbdf1:

- Mtk.crasher enters its transition attempts when enforcecrash is set, MEID is
  missing, or the mode flag is not BROM. It invokes an exploit-specific delegate
  and reinitializes connections. The final return is not a terminal assertion
  that BROM was reached. Caller/backend behavior still matters.
- bypass_security invokes that path and then a RAM payload path. A known SoC
  entry in a config table does not qualify a USB-only transition on this
  installed PL7/LK3/TEE262 state. No transition was attempted here.
- Preloader.init is not passive USB enumeration: it performs a protocol
  handshake and hardware/security queries and conditionally disables a watchdog.
  reset_to_brom contains register-write calls. Direct absence of an eMMC-write
  method does not prove whole-firmware persistence-free behavior or recovery.
- The initializer also reads identifiers, writes host settings and logs some
  values. Future collected evidence needs an explicit private/sanitized path;
  do not paste raw helper output into the public repository. No actual identifier
  values were collected by this review.

The watchdog condition is retained as source syntax. The helper's has64bit field
controls its internal branch; it is not an independent CPU-ISA probe. Likewise,
stock Fire OS/PL/LK properties do not supply protocol-observed hardware code,
subcode/version, starting BROM/preloader mode or SBC/SLA/DAA security facts.
These remain exact missing observations for entry qualification.

The get_hw_sw_ver caller contains a sentinel branch, but the current getter
immediately unpacks its response: a transport failure can raise before the
caller's later assignments. Do not infer a clean recoverable failure return
solely from the sentinel check, or turn zero-valued version fields into proof
that a particular DA record is compatible. Error/re-entry behavior remains
unobserved. No new hard Android/kernel feasibility blocker is asserted here.

Entry alternatives now have a precise boundary: already-in-mode, software
transition attempts, and hardware-assisted entry must be evaluated separately.
The hardware preference question chooses planning scope, not permission to run
any of them. Preserve the actual starting-state provenance and failure/re-entry
logs before calling a route qualified. Parent106 stays open.

Next independent source task is the candidate DA's memory-initialization input:
inspect whether the already cached exact current stock preloader supplies the
expected EMI data format, without executing it, patching it or flashing an older
component. A data-format match alone will not establish safe agent execution.
