# Forced-argument precompile review

The hash-checked known-static-source inventory has seven distinct keys. It is
not complete effective runtime evidence: authorized stock collection could not
read /proc/cmdline, and all LK mutations/boot modes have not been traced. The
forced device profile remains uncompiled and is not recommended for a device
test or physical package on this evidence.

- console/earlycon: replaced intentionally by the opt-in profile. Actual firmware
  UART state and electrical routing remain separate unknowns.
- root: stock /dev/ram selection is distinct from the isolated bundled /init.
  The diagnostic omits block support and uses its independent initramfs. Do not
  carry stock root/media assumptions into that experiment.
- initrd: the static legacy address/size is not a safe modern placement contract.
  Preserve a separately established DT/initrd/reservation handoff, not a copied
  legacy argument. Pinned fdt.c calls its initrd/elfcore readers before command
  line selection; that ordering does not validate addresses or loader delivery.
- vmalloc: its stock value is an old kernel input, not a proven constraint for
  this ACK build. Consumer/effect compatibility remains unaudited here.
- androidboot.hardware: a stock Android identity input. The isolated reporter is
  not Android userspace; that does not establish all possible kernel consumers.
- bootopt: present in the original stock header used by the loader path. Its
  pre-entry interpretation and complete version-specific behavior remain open.
  A kernel FORCE setting cannot retroactively alter loader decisions made
  before kernel entry.

No mem/nr_cpus/maxcpus keys occur in these specific static sources. Do not infer
that no runtime-generated memory/security constraint exists. CMDLINE_FORCE can
solve an argument-conflict mechanism only after kernel entry, not the firmware
handoff contract. Do not represent this review as permission to discard unknown
firmware constraints.

Next use a **generic QEMU-only analogue** to test forced argument selection with
contradictory incoming arguments and sanitized reporter evidence. It must use
QEMU's PL011 console, not the tablet MMIO address; neither run the douglas profile
on virt nor claim generic success validates discarded tablet constraints. This
can establish actual kernel mechanism behavior independently while physical
entry/restore/UART gates remain blocked.

A new compile must retain source/config/Image/initramfs/log digests and record
whether requested limits actually win. Use the existing gated build resource
budget (approximately0.3GiB source download,15GiB free disk,7GiB available RAM,
60-minute job timeout; previous run approximately24minutes). No new paid runner,
full Android checkout or tablet operation. No compile started for this review.

Reproduce the cached static inventory with
`python3 scripts/audit_forced_argument_inputs.py`; output publishes keys and
hashes only. No raw private runtime command line is accessed or published.
