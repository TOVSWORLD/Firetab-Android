#!/usr/bin/env bash
# Earlier baseline hashes are pre-SYM827; only final marker qualifies this scope.
set -euo pipefail
[[ "${ARGUMENT_PROFILE:-none}" = none ]] || exit 2
bash scripts/build_ack_baseline.sh diagnostic
readonly root="$PWD/work/ack-baseline"
readonly output="$root/output"
python3 scripts/apply_sym827_port.py "$root/source"
grep -qx CONFIG_REGULATOR_FAN53555=y "$output/.config"
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" W=1 drivers/regulator/fan53555.o
sha256sum "$output/drivers/regulator/fan53555.o"
echo MT8163_SYM827_OBJECT_COMPILE_COMPLETE
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" Image vmlinux
sha256sum "$root/source/drivers/regulator/fan53555.c" "$output/.config" "$output/vmlinux" "$output/arch/arm64/boot/Image"
wc -c "$output/arch/arm64/boot/Image"
echo MT8163_SYM827_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED
