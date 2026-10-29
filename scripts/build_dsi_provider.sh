#!/usr/bin/env bash
# Earlier Images are pre-DSI. Only the distinct final marker qualifies this scope.
set -euo pipefail
[[ "${ARGUMENT_PROFILE:-none}" = none ]] || exit 2
bash scripts/build_mipi_provider.sh
readonly root="$PWD/work/ack-baseline"
readonly output="$root/output"
python3 scripts/apply_dsi_port.py "$root/source"
"$root/source/scripts/config" --file "$output/.config" --enable DRM --enable DRM_MEDIATEK --enable MTK_MMSYS
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 olddefconfig
for symbol in DRM DRM_MEDIATEK DRM_MIPI_DSI DRM_PANEL DRM_KMS_HELPER DRM_DISPLAY_HELPER DRM_BRIDGE_CONNECTOR VIDEOMODE_HELPERS MTK_MMSYS PHY_MTK_MIPI_DSI RESET_CONTROLLER ARCH_MEDIATEK COMMON_CLK OF GENERIC_PHY; do
  grep -qx "CONFIG_${symbol}=y" "$output/.config"
done
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" W=1 drivers/gpu/drm/mediatek/mtk_dsi.o drivers/gpu/drm/mediatek/mtk_drm_drv.o
sha256sum "$output/drivers/gpu/drm/mediatek/mtk_dsi.o" "$output/drivers/gpu/drm/mediatek/mtk_drm_drv.o"
echo MT8163_DSI_PROVIDER_OBJECT_COMPILE_COMPLETE
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$(nproc)" Image vmlinux
sha256sum "$root/source/drivers/gpu/drm/mediatek/mtk_dsi.c" "$root/source/drivers/gpu/drm/mediatek/mtk_drm_drv.c" "$root/source/drivers/gpu/drm/mediatek/mtk_dsi_mt8163.h" "$output/.config" "$output/vmlinux" "$output/arch/arm64/boot/Image"
wc -c "$output/arch/arm64/boot/Image"
cat "$output/.config"
echo MT8163_DSI_PROVIDER_IMAGE_COMPLETE_RUNTIME_UNQUALIFIED
