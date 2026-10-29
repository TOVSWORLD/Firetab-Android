# Display-PWM source prerequisites

Updates #27. No kernel variant, binding support, backlight or electrical behavior
is admitted by this finite audit. Reproduce `python3 scripts/audit_disp_pwm_source.py
--check`. Exact ACK d9318bdb and donor20951722 drivers are byte-identical8532B,
with MT8173 data but no explicit MT8163 match. Exact legacy e0a3a2b code/header,
register definitions and clock-helper source are cached and hash-locked.

Actual selected C is compiled under ASan/UBSan with RAM clock/register/platform
callbacks. Pinned PWM core `pwm_state_valid` and `__pwm_apply` execute unchanged:
non-waveform provider and CONFIG_PWM_DEBUG disabled match the tested driver ops.
The core permits disabled states with irrelevant period/duty values. Changing a
cached-off disabled state reaches the driver, which acquires clocks/programs
registers/enables output and returns success. Core then caches enabled=false,
while driver/RAM enable is true. The unchanged-state shortcut is tested in the
actual core path; these witnesses use changed states and are not mere invalid
callback injection. Enabled zero-period inputs are rejected by core.

Actual driver apply programs encoded period=cycles-1, whereas get_state uses the
raw encoded value without +1.4096 raw values demonstrate this isolated readback
arithmetic difference at a synthetic1GHz rate; no measured waveform is asserted.
A core-valid period `(1ULL<<44)+1024` at that rate wraps the32-bit divider before
its range guard and programs1024 cycles with success. The mul/div mock uses128-bit
intermediate arithmetic; this witness's quotient fits64 bits. Rate-zero apply
can enable; get_state reaches a zero-denominator helper twice. The helper is
instrumented to record/return, so neither actual kernel division nor a device
failure/panic was executed. Main/MM clock failures, cleanup and five probe error
stages also execute. Kernel CCF/devres/concurrency are not simulated.

Both source dividers use0x3ff (10 bits), despite the modern comment saying11.
Legacy active initialization updates period mask0x3ff; modern uses0xfff. Actual
operations agree16384/65536 low-word states at the chosen1024-cycle setup, with
mask difference0xc00. Legacy duty uses0x1fff and commit performs full-word1→0;
modern commit updates bit0 only, agreeing2/65536 initial low-word states. These
are exhaustive isolated word controls, not hardware width, probability, timing
or whole-sequence equivalence. A subset mask does not establish that larger
hardware fields are supported. Legacy three-clock on/off order is traced and
injected negative API returns are discarded; exact helper returns int and can
return-1. This is not proof any actual clock failed.

The queued lead calling the PWM node disabled was wrong: the fresh accepted DTB
has `/soc/pwm@14014000` status="okay" and compatible MT8163+MT8173 fallback.
No DT state was changed. Actual clock tuples are MMSYS33(main PWM26M) and32(mm),
MM domain0. ID values are clock arguments, not additional phandles. Compiled clock
source gates these from clk26m/mm_sel; legacy also prepares TOP_PWM_SEL. Neither
clock callback trace nor declaration establishes delivered rate or sequencing.
Prior DSI Image config has PWM_MTK_DISP=m, not builtin PWM/object qualification.
All loading/physical trials remain denied; no PWM/backlight action occurred.

Next actual source implementation should fix the settled error findings through
an explicit MT8163 boundary with checked disabled/rate/64-bit arithmetic,
reference/cache/error ownership and readback, preserving other SoC bodies.
Establish a conservative source-derived field/commit policy before choosing the
variant; do not guess MT8173 equivalence or widen fields from comments. Require
actual patched-C failure/ordering/register/core-caller/old-SoC controls, locked
all-output patch preflight, explicit builtin PWM real object/config/final Image
before merge or matched binding claims. Whole legacy three-clock delivery and
physical output remain independent gates, not a reason to run hardware helpers.

PR434 is accepted43e35858 after five checks at5188f99/481 actual CI tests,40
metadata controls and two fresh source-DTB guards. Its normalized CI receipt is
now public in evidence/dsi-binding/ci-result.json. Current full canonical30 and
isolated24 contexts remain failed; DSI missing graph/master/panel and all physical
loading/independent failed-return/retained-log/thermal/regulator gates stay open.
