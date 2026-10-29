#!/usr/bin/env bash
# Prior Image hashes are pre-MIPI; only the final MIPI marker qualifies this scope.
set -euo pipefail
[[ "${ARGUMENT_PROFILE:-none}" = none ]] || exit 2
bash scripts/build_sym827_provider.sh
readonly root="$PWD/work/ack-baseline"
readonly output="$root/output"
python3 scripts/apply_mipi_port.py "$root/source"
"$root/source/scripts/config" --file "$output/.config" --enable PHY_MTK_MIPI_DSI --enable RESET_CONTROLLER
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 olddefconfig
for symbol in PHY_MTK_MIPI_DSI ARCH_MEDIATEK COMMON_CLK OF GENERIC_PHY RESET_CONTROLLER MTK_INFRACFG COMMON_CLK_MT8163 REGULATOR_FAN53555; do
  grep -qx "CONFIG_${symbol}=y" "$output/.config"
done
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" W=1 drivers/phy/mediatek/phy-mtk-mipi-dsi.o drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.o drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.o
sha256sum "$output/drivers/phy/mediatek/phy-mtk-mipi-dsi.o" "$output/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.o" "$output/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8183.o"
echo MT8163_MIPI_PROVIDER_OBJECT_COMPILE_COMPLETE
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" Image vmlinux
sha256sum "$root/source/drivers/phy/mediatek/phy-mtk-mipi-dsi.c" "$root/source/drivers/phy/mediatek/phy-mtk-mipi-dsi-mt8173.c" "$root/source/drivers/phy/mediatek/phy-mtk-mipi-dsi.h" "$output/.config" "$output/vmlinux" "$output/arch/arm64/boot/Image"
wc -c "$output/arch/arm64/boot/Image"
cat "$output/.config"
echo MT8163_MIPI_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED
