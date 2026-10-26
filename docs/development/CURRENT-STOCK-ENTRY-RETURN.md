# Current-stock douglas: entry and return route review

Reviewed2026-10-26. Target evidence remains build50.6.5.9_user_659664620,
PL7/LK3/TEE262; displayed Fire OS5.7.1.0 is not a substitute for those component
versions. No tablet was accessed and no helper was executed in this review.

## What the public USB-only guide actually establishes

The pinned [FireHD8-2017 guide](https://github.com/ryanfortner/FireHD8-2017/blob/91f93505eee47d6848dc6e161f29011503106a33/README.md)
reports the author's5.7.0.0/Linux setup. Its route uses intentional bricking,
then BootROM minimal and modified fastboot. It is not a read-only USB transition
or evidence of interrupted-query return on this exact build. The README's broad
recoverability reassurance is not an independently verified restore mechanism.
Its later bootloader/recovery success depends on completing the modifying chain.

The already inspected [sequence inventory](../../evidence/recovery-material/sequence-gates.json)
shows why the initial bootstrap and eventual recovery are separate: the minimal
path assumes prior changes and writes boot/security-related state, including
RPMB. A boot/user-region escrow cannot promise to restore that security state.
Current versus older official EMI identity resolves only memory-data provenance.
It does not make this sequence suitable for the first observation or backup.

## Remaining candidate routes and exact missing evidence

- **Stock recovery → stock fastboot:** potentially an observation starting point,
  not automatically BootROM or a RAM-loading capability. Exact current command
  acceptance, signature policy and normal-return behavior remain unknown. A
  guide reaching fastboot does not establish arbitrary boot support. No command
  was sent. A future test must distinguish OS reboot, USB reset, boot command,
  flash command and actual kernel handoff in its effect inventory.
- **Preloader protocol → BootROM:** the reviewed MTKClient candidate can invoke
  crash/reset/bootstrap behavior; that is not passive observation. Exact entry
  on this build and interrupted-attempt return are unverified. The owned minimal
  collector intentionally omits those transitions and cannot create reachability.
- **Hardware BootROM entry:** owner preference is pending; no traceable current
  board-specific point/electrical/entry-and-return procedure is qualified. Generic
  MediaTek advice or another Fire generation does not fill that gap. No opening,
  shorting, cable operation or measurement is requested.
- **Already modified recovery:** useful later, but not an established starting
  state on this stock tablet. An existing Android10 port does not prove the stock
  boot chain accepts the new diagnostic package without prerequisite changes.

The primary XDA page returned502 during this bounded refresh; the postmarketOS
page redirected to an inaccessible host. These access failures do not prove
missing methods or incompatibility. Search results were not promoted to verified
instructions. No full firmware/helper archive was downloaded.

## Direction and next source task

There is no newly verified non-destructive exact-build entry/return route from
this refresh. Keep106 open. Do not claim the host observation adapter has solved
entry merely because its synthetic tests and native version call pass.

Next inspect the cached current LK's stock fastboot handler inventory and boot
image verification path, recording source/disassembly identities and command
availability as static evidence only. Determine whether a RAM-only boot path
exists before planning a physical command. Do not publish raw firmware windows
or infer acceptance from command-name strings alone. A concrete owner test must
state what can change and how stock operation is restored after its failure.
