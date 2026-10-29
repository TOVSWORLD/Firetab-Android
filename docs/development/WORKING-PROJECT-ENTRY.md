# Working Douglas projects: entry and recovery reconciliation — #439

Reviewed29 October2026 from the original authors' rendered XDA pages, project
releases and cached source. Earlier403/502 web-fetch failures were access failures;
the browser successfully read the original pages today. No tablet/helper ran and
no archive/binary was downloaded. This supplements the earlier NO-GO decision:
**opening the case is not an established prerequisite.** Keep#439 Active and#345
conditional while reconciling the documented software route.

## Original unlock documentation

[k4y0z's Douglas guide, posts1/3](https://xdaforums.com/t/unlock-root-twrp-unbrick-fire-hd-8-2017-douglas.3962846/)
describes case-closed installation, with hardware access a possible failure
fallback. It requires Linux and USB, changes GPT and wipes data. The rooted
step1 path branches above5.6.4.0 into temporary bricking/downgrade. Its expanded
warning distinguishes separate brick scripts from step1: **external brick scripts
require the full BootROM step, not minimal**. TWRP then installs ROMs onto remapped
boot/recovery targets; hacked fastboot and stock recovery are later states,
not capabilities established on this stock unit. The stock-return instructions
depend on that changed environment.

The PL6/LK2/TEE259 values in cached step1 are branch limits, not proof the entire
published method is impossible on newer firmware. Observed PL7/LK3/TEE262 selects
the risky downgrade branch if that rooted script is usable. It does not qualify
root access, the separate fastboot brick operation or its failure exit.

## A concrete instruction conflict

The cached original brick archive's `amonet/brick-9820.sh` ends by directing the
user to minimal mode. This conflicts with the expanded author warning above.
The cache path and SHA are pinned in
[evidence](../../evidence/working-project-entry/review.json); this file was read
as text, never invoked. The earlier archive receipt also inventories both full
and minimal scripts. The warning must not be flattened into one generic recipe.

[Recent thread page47](https://xdaforums.com/t/unlock-root-twrp-unbrick-fire-hd-8-2017-douglas.3962846/page-47)
contains reports923/925/926 pairing the external brick9820 script with minimal
mode before failures. These are individual reports, not controlled causation or
failure-rate data. Post929 asks about5.7.1.0; no response follows on that reviewed
page. It neither proves incompatibility nor supplies current-build success.

Do not run a copied command list, treat script completion as successful rescue,
or silently substitute the full helper. Both paths have persistent effects.
A corrected printed instruction alone does not validate the other payloads,
installed boot-chain acceptance or independent recovery. No script is patched or
executed by this review; the published warning is an input to the route proposal.

## Working ROMs and their prerequisites

[Rortiz2's LineageOS17.1 thread](https://xdaforums.com/t/rom-unofficial-10-lineageos-17-1-for-amazon-fire-hd8-7-6th-gen-douglas-giza.4474959/)
links the Douglas unlock guide and project sources. Its recovery installation
presumes the earlier unlock/TWRP transition. Its bug instructions distinguish
live logcat from pre-reboot kernel evidence. Reading `/proc/last_kmsg` is a
recommendation for that ROM, not proof stock permissions or new-kernel retention.
The old thread's issue list must not be treated as the latest project capability.

The author now links a
[LineageOS18.1 thread](https://xdaforums.com/t/rom-unofficial-11-lineageos-18-1-for-amazon-fire-hd8-7-6th-gen-douglas-giza.4806454/).
It explicitly requires an unlocked bootloader and TWRP, reports broad functionality
including cameras/decoding, lists WidevineL1 as a known issue and points to
[amazon-oss](https://github.com/amazon-oss). Repository metadata shows device-common,
kernel and vendor-common default branches named lineage-18.1. These are maintainer
claims and source leads, not tests on our unit or proof our maintained kernel works.
No ROM/GApps/Magisk was installed or downloaded. Optional rooting is not selected.

## Source packaging and recovery details we can reuse

Cached Douglas BoardConfig identifies its board and kernel config; common config
specifies legacy header/page/offset fields and `Image.gz-dtb`. These are concrete
packaging inputs for comparison with our maintained kernel, not a reason to copy
legacy addresses blindly. The common recovery fix script reads exploit headers/
payloads from boot_amonet/recovery_amonet and can write the boot copy. Thus recovery
protection presumes that modified layout and working recovery; it is not an
independent rescue for an unentered or failed initial unlock. All cited source
files/commits are hashed in the review receipt.

The legacy common command line includes permissive SELinux. That is historical
configuration, not a proposed change to this project's security requirements.
Source reuse must preserve enforcing security. Kernel source changes are not
needed to establish today's documented entry distinction.

## Next executable engineering action

Continue **inside#439** with a source-only, reviewable software-unlock proposal
for the original external-brick/full-BootROM branch. Reuse the retained original
archive and existing write-extent/return reviews. Identify exact package/helper
pairing, required host environment, installed-build acceptance evidence, mutation
boundaries and an independently reachable failure exit before proposing execution.
The useful finding is the public instruction conflict—not another LK microtrace,
stock capture, ADB port survey or synthetic readiness test.

The proposal must explicitly say where present evidence stops. Any later
preloader/LK/TEE/RPMB downgrade/write remains high brick risk and needs approval
of a concrete procedure. Opening is neither selected nor proven necessary; a
possible hardware fallback is a risk of the software proposal, not an automatic
work item. #347/#346/#348 remain unqualified. If the software proposal cannot be
made credible, bring its precise unresolved risk to the owner rather than claiming
all software routes are impossible or resuming peripherals.
