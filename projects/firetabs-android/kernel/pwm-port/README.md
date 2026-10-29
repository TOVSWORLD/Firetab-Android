# Scoped MT8163 PWM source policy

Updates #27. This implements a conservative MT8163 source policy; it does not
establish hardware field width, output timing, panel/backlight readiness or safe
experimental loading. Candidate PWM status remains okay, exactly as in the
accepted DTB. No DT, binding, device, GPIO, clock or backlight action occurred.

The explicit MT8163 descriptor selects new callbacks. Existing three descriptors,
ops initializer and function bodies remain byte-identical through legacy helper
dispatch. No global PWM core change or blind MT8173 alias is used. Policy source:
legacy e0a3a2b active writes demonstrate10-bit divider/period,13-bit duty and full
commit word1→0; this implementation limits itself to that period range, preserves
other control bits and rejects pre-existing bits11:10 rather than reinterpreting
or clearing a potentially wider configuration. This is a software support limit,
not a physical hardware maximum. The full commit write intentionally follows
legacy and is distinct from generic bit0 RMW. No third TOP_PWM_SEL clock is added
or claimed equivalent to current main/MM gate declarations.

Disabled requests ignore irrelevant timing/polarity, acquire checked references
only to write off/commit and release them, and never enable. Enabled requests
check polarity, positive period, duty≤period, nonzero rate,64-bit products/cycles/
divider/period/duty and source range before narrowing or driver MMIO. Invalid
updates preserve a previous successful request and its references/cache. Readback
adds the encoded+1, rejects wider or impossible encodings, does not divide by
zero, and uses quotient/remainder ceiling without an overflowing numerator+rate.
Errors leave caller output unchanged. Requested core cache and rounded hardware
readback are distinct; no host test observes an actual waveform.

Main/MM references are acquired and released by explicit ownership, with reverse
cleanup of newly acquired resources on failure. A mutex serializes the scoped
callbacks. Probe validates resource alignment/minimum0x18 and power-domain
presence, rejects unqualified assigned-clock overrides, and initializes state
before publication. A devm action registered before pwmchip_add runs after chip
removal and before earlier clock/allocation releases under the normal devres
contract. Failed registration explicitly cleans any references acquired during
publication; later cleanup is idempotent. Cleanup never acquires clocks merely
to stop hardware this instance did not own. Partial ownership latches a fault,
avoids unsafe MMIO and releases only its owned references; it does not claim the
physical output was stopped. Real devres ordering/concurrency/clock delivery and
reprobe remain unqualified beyond these source/native controls. Clock disable
APIs are void; their calls cannot prove electrical shutdown or report failure.

`apply_pwm_port.py` hash-checks pinned original driver, new helper, core/header,
Kconfig/Makefile, policy and patch. It shadow-applies and verifies every output
before source writes; wrong inputs, unexpected existing header, wrong outputs
and reapply reject without changing targets. This preflight is not crash-atomic
filesystem persistence or concurrent-checkout protection.

`audit_pwm_port.py` compiles the actual shadow-patched helper/private structures,
selected legacy bodies and actual PWM core caller under ASan/UBSan. RAM controls
exercise source-reproducers, arithmetic limits/26MHz quantization, get_state/error
output, refs/cleanup/probe publication errors, six probe stages, MMIO/cache write
order,65536 preservation states and all older descriptors. Legacy GPIO branches,
kernel CCF/devres/electrical semantics are not simulated.

The new pwm-provider wrapper stages unchanged DSI/MIPI/SYM/baseline scripts,
requests builtin PWM/PWM_MTK_DISP/dependencies, probes the real pwm-mtk-disp.o W=1
and links final Image/vmlinux/config. Only final
MT8163_PWM_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED plus hashes qualifies this
scope. Prior staged Images/gzip/PWM=m are pre-PWM; explicit object hash is pre-Image,
not asserted final linked bytes. New exact-head Linux build and all PR checks are
required before merge or source-matched binding publication. No QEMU/device claim.

PR435 source audit accepted32979e5a/483 CI tests; its final receipt is included in
evidence/disp-pwm-source/ci-result.json. Full metadata contexts remain30/24 failed;
all physical loading, independent failed-return, retained-log, thermal, regulator,
DSI master/panel and beta admission gates stay open. SELinux/security unchanged.
