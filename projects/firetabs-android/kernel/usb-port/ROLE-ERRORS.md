# MT8163-scoped MUSB role/init errors — #27

The actual MUSB patch adds an exact mediatek,mt8163-musb OF match with strict
role-error data. The generic fallback has no strict data. Its previous role,
set_mode, init and exit functions remain byte-identical after renaming to legacy
helpers; non-MT8163 dispatch retains their behavior. The existing T-PHY analog
patch is unchanged. Both source targets now have original/output hash locks and
are shadow-applied/output-checked before any real source writes.

The strict role path validates the requested role, rejects an unready PHY and
rejects all transactions after a latched fault. It obtains needed PHY power and
sets the requested mode before publishing controller register/OTG/software state.
Transition to NONE powers off only after its mode call succeeds. A successful
transaction then commits session/role state. Power/init bookkeeping prevents
duplicating the reference already acquired by init while the initial OTG role is
NONE. A NONE request also reconciles that initially powered idle state.

On a failed mode or power-off call, the helper attempts the previous mode. If it
newly acquired power, it attempts to release only that reference. The primary
operation error is returned even when cleanup also fails; cleanup errors are
logged separately. No controller/OTG/advertised role commit occurs on failure.
Every PHY failure latches the role as unqualified for this glue instance, even
when cleanup returned success. Getter returns NONE for a faulted/unready strict
instance; subsequent requests fail EIO rather than treating a repeated role as
success. NONE here is a conservative API value, not proof of physical disconnect.

The normal set_mode caller propagates the scoped role-helper result. Strict init
checks phy_init, power_on and set_mode; a failure unwinds its known references
and unregisters any role switch before returning, without enabling interrupts.
Power-off failure stops cleanup before phy_exit, preserving the PHY core's stated
ordering contract. Strict exit uses the same bookkeeping and avoids double-off
after a role transition to NONE. On cleanup failure it returns the error without
claiming clocks/runtime-PM teardown completed. Faults are not automatically cleared.
Safe reprobe/provider recovery, concurrent callback behavior and physical rollback
remain unqualified; the tests model serialized API calls only.

The pinned ACK PHY core confirms that init/power references increment only on
success, failed exit/power_off retain their counters, and mode attributes update
only on successful set_mode. Its capped31489-byte official read and hash are in
evidence/usb-role-errors. Backend hardware may have partially changed despite an
API error; software restoration/counter tests never establish electrical recovery.

The actual patched functions compile with Wall/Wextra/Werror and execute with
RAM-only register/backend mocks. Controls cover twelve successful prior-power/
target combinations and idempotency, init-powered NONE without duplicate power,
initial/caller errors, mode-restoration/power-cleanup/exit failures, unchanged
register/role state on failure, original error preservation, role getter/fault
behavior, all init cleanup phases, interrupt enable ordering, and static
peripheral init/exit without a nonexistent role switch. Separate controls retain
the generic ignored-error behavior and byte-identical legacy functions.

The apply tool verifies revision, all original sources, helper/definition and
patch hashes, exact target set and every expected shadow output before applying
the full set to the real disposable tree. Wrong second-source or output hash
controls verify both actual files remain unchanged. This is all-target preflight,
not a guarantee against arbitrary host filesystem failure during final writes.

A new exact-head usb-providers Linux object/config/Image run is required before
merge; PR416's older build cannot qualify this MUSB change. No QEMU/device/mode
execution is requested. Both disabled DTs and canonical34/isolated28 failing
binding contexts remain unchanged. Gadget packaging/configuration and all
analog/clock/physical USB/loading/independent return/log gates remain open.
