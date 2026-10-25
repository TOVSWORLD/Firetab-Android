#!/usr/bin/env bash
# Generic compile diagnostic only; does not produce douglas firmware.
set -euo pipefail
readonly revision=d9318bdb4c34e8b2d997b4f67ced56b120b22b87
readonly mode="${1:-generic}"
[[ "$mode" = generic || "$mode" = clocks ]] || exit 2
readonly root="$PWD/work/ack-baseline"
[ "$(uname -s)" = Linux ] || { echo 'A Linux build host is required'; exit 2; }
for tool in git make clang-18 ld.lld-18 llvm-ar-18 bison flex bc openssl pahole; do
  command -v "$tool" || exit 2
done
free -h
df -h .
[ "$(df -Pk . | awk 'END {print $4}')" -ge 15728640 ] || { echo 'Need 15 GiB free'; exit 2; }
[ "$(awk '/MemTotal:/ {print $2}' /proc/meminfo)" -ge 7340032 ] || { echo 'Need 7 GiB RAM'; exit 2; }
mkdir -p "$root"
[ ! -e "$root/source" ] || { echo 'Refusing to overwrite an existing checkout'; exit 2; }
git init "$root/source"
git -C "$root/source" remote add origin https://android.googlesource.com/kernel/common
# A shallow single revision fetch; no tags or full history. Budget is checked
# after transfer; hosted runner timeout also bounds stalled network/build work.
git -C "$root/source" -c http.lowSpeedLimit=1024 -c http.lowSpeedTime=120 fetch --depth=1 --no-tags origin "$revision"
[ "$(du -sk "$root/source/.git" | awk '{print $1}')" -le 3145728 ] || { echo 'Fetch exceeded 3 GiB budget'; exit 2; }
git -C "$root/source" checkout --detach FETCH_HEAD
[ "$(git -C "$root/source" rev-parse HEAD)" = "$revision" ]
clang-18 --version
ld.lld-18 --version
make --version | head -1
readonly output="$root/output"
readonly jobs="$(nproc)"
# Upstream ARM64 defconfig deliberately establishes a generic compiler baseline.
# It is not Android GKI configuration and not a douglas driver configuration.
if [ "$mode" = clocks ]; then
  python3 scripts/apply_clock_port.py "$root/source"
fi
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 defconfig
if [ "$mode" = clocks ]; then
  for symbol in COMMON_CLK_MT8163 COMMON_CLK_MT8163_AUDSYS COMMON_CLK_MT8163_IMGSYS COMMON_CLK_MT8163_MFGCFG COMMON_CLK_MT8163_MMSYS COMMON_CLK_MT8163_VDECSYS COMMON_CLK_MT8163_VENCSYS; do
    "$root/source/scripts/config" --file "$output/.config" --enable "$symbol"
  done
  make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 olddefconfig
  for symbol in COMMON_CLK_MT8163 COMMON_CLK_MT8163_AUDSYS COMMON_CLK_MT8163_IMGSYS COMMON_CLK_MT8163_MFGCFG COMMON_CLK_MT8163_MMSYS COMMON_CLK_MT8163_VDECSYS COMMON_CLK_MT8163_VENCSYS; do
    grep -qx "CONFIG_${symbol}=y" "$output/.config"
  done
  make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" W=1 drivers/clk/mediatek/
fi
make -C "$root/source" O="$output" ARCH=arm64 LLVM=-18 -j"$jobs" Image vmlinux
file "$output/vmlinux" "$output/arch/arm64/boot/Image"
llvm-readelf-18 -h "$output/vmlinux"
sha256sum "$output/.config" "$output/vmlinux" "$output/arch/arm64/boot/Image"
wc -c "$output/vmlinux" "$output/arch/arm64/boot/Image"
grep -E '^CONFIG_(ARM64|ARM64_4K_PAGES|COMPAT|ARCH_MEDIATEK|SECURITY_SELINUX|BPF_SYSCALL|ANDROID_BINDER_IPC)=' "$output/.config"
# Emit complete resolved configuration in CI logs for this first experiment.
cat "$output/.config"
echo "ARM64_COMPILE_COMPLETE mode=$mode; DOUGLAS_BOOT_UNTESTED"
