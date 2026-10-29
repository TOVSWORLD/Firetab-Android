#!/usr/bin/env bash
# All earlier Images are pre-PWM; only the final distinct marker qualifies this scope.
set -euo pipefail
[[ "${ARGUMENT_PROFILE:-none}" = none ]] || exit 2
bash scripts/build_dsi_provider.sh
readonly root="$PWD/work/ack-baseline"
readonly output="$root/output"
python3 scripts/apply_pwm_port.py "$root/source"
"$root/source/scripts/config" --file "$output/.config" --enable PWM --enable PWM_MTK_DISP
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 olddefconfig
for symbol in PWM PWM_MTK_DISP HAS_IOMEM ARCH_MEDIATEK COMMON_CLK OF MTK_MMSYS DRM_MEDIATEK PHY_MTK_MIPI_DSI; do
  grep -qx "CONFIG_${symbol}=y" "$output/.config"
done
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" W=1 drivers/pwm/pwm-mtk-disp.o
sha256sum "$output/drivers/pwm/pwm-mtk-disp.o"
echo MT8163_PWM_PROVIDER_OBJECT_COMPILE_COMPLETE
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" Image vmlinux
sha256sum "$root/source/drivers/pwm/pwm-mtk-disp.c" "$root/source/drivers/pwm/mtk_pwm_mt8163.h" "$output/.config" "$output/vmlinux" "$output/arch/arm64/boot/Image"
wc -c "$output/arch/arm64/boot/Image"
cat "$output/.config"
echo MT8163_PWM_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED
