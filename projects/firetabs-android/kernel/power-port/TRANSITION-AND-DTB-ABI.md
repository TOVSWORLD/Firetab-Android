# Power/clock transition trace and observed stock DT ABI — #20/#347

A bounded read-only ADB capture confirmed douglas, the known stock incremental
and completed Android boot. Whitelisted DT properties in sysfs and procfs agree:
scpsys clock names are `mfg`, `mm`, cells are `<6 70 6 67>`, and topckgen declares
phandle6 with one clock cell. No root, mode change or firmware operation occurred.
The first command used unavailable `head`; command-error bytes were rejected.
Available `cat` with host byte/time bounds succeeded. This was not evidence of
USB reads requiring root. Raw transport data/selectors remain ignored/private;
normalized receipt: `evidence/power-port/transition-order/observed-stock-clock-abi.json`.

Legacy MFG/MM binding IDs70/67 match those observed properties. Candidate IDs are
54/51. Candidate IDs70/67 mean SCAM/ATB, so valid-looking integer clock cells are
not sufficient compatibility evidence. The source MFG mux fields agree, and its
legacy parents resolve through three1:1 aliases to candidate parents; this does
not measure rates, selected parents or hardware transitions. The observed stock
scpsys tuple also differs from the candidate simple-mfd/child model. Only selected
live properties were captured, not the full live tree.

The fresh-DTB power guard now resolves the actual topckgen phandle/cell contract
and requires candidate MM/MFG IDs from the matching bundled header. It rejects
stock IDs and a wrong clock-provider phandle even when cell counts look valid.
Loader qualification must demonstrate handoff of the matching candidate DTB;
stock DTB substitution or a two-number rewrite is not a qualified loading route.
No experimental handoff, failure return or retained log is demonstrated here.

`python3 scripts/audit_power_transition_order.py --check` traces literal normal
non-modem/non-RTFF success paths. Main power-on control writes agree. Power-off
writes differ: legacy resets before clock disable and clears ON before ON_2ND;
ACK disables clocks before reset and clears ON_2ND before ON. Basic clocks are
enabled before each local power-on sequence and disabled after off acknowledgement,
but ownership moves from MFG to MFG_ASYNC. This changes the clock lifetime boundary;
no timing, global callback-order or hardware equivalence is inferred.

The legacy wakeup Boolean tables are Python models of checked legacy C predicates,
not executed kernel tests. ACK's header describes ACTIVE_WAKEUP retention, but its
genpd implementation has not been acquired from the attempted pinned endpoints.
Header comments alone do not justify changing capabilities. Current hardware
wakeup, power timing and partial-failure cleanup remain unqualified.

Exact revisions, source hashes, observed metadata and comparison/guard results
are in `evidence/power-port/transition-order/`. Source drift tests reject changed
mux fields and non-unit aliases. No driver policy, DT property or device behavior
is changed by this investigation.
