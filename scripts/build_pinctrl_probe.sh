#!/usr/bin/env bash
# Object-only Linux compile probe; no firmware packaging/device access.
set -euo pipefail
readonly revision=d9318bdb4c34e8b2d997b4f67ced56b120b22b87
readonly root="$PWD/work/pinctrl-probe"
[ "$(uname -s)" = Linux ] || exit 2
for tool in git make clang-18 ld.lld-18 llvm-ar-18 bison flex bc openssl pahole; do command -v "$tool"; done
free -h
df -h .
[ "$(df -Pk . | awk 'END {print $4}')" -ge 15728640 ] || exit 2
[ "$(awk '/MemTotal:/ {print $2}' /proc/meminfo)" -ge 7340032 ] || exit 2
mkdir -p "$root"
[ ! -e "$root/source" ] || { echo 'Refusing existing checkout'; exit 2; }
git init "$root/source"
git -C "$root/source" remote add origin https://android.googlesource.com/kernel/common
git -C "$root/source" -c http.lowSpeedLimit=1024 -c http.lowSpeedTime=120 fetch --depth=1 --no-tags origin "$revision"
[ "$(du -sk "$root/source/.git" | awk '{print $1}')" -le 3145728 ] || exit 2
du -sk "$root/source/.git"
git -C "$root/source" checkout --detach FETCH_HEAD
du -sk "$root/source"
python3 scripts/apply_pinctrl_port.py "$root/source"
clang-18 --version
ld.lld-18 --version
make -C "$root/source" O="$root/output" ARCH=arm64 LLVM=-18 defconfig
"$root/source/scripts/config" --file "$root/output/.config" --enable PINCTRL_MT8163
make -C "$root/source" O="$root/output" ARCH=arm64 LLVM=-18 olddefconfig
grep -qx CONFIG_PINCTRL_MT8163=y "$root/output/.config"
make -C "$root/source" O="$root/output" ARCH=arm64 LLVM=-18 -j"$(nproc)" W=1 drivers/pinctrl/mediatek/
file "$root/output/drivers/pinctrl/mediatek/pinctrl-mt8163.o"
llvm-readelf-18 -h "$root/output/drivers/pinctrl/mediatek/pinctrl-mt8163.o"
sha256sum "$root/output/.config" "$root/output/drivers/pinctrl/mediatek/pinctrl-mt8163.o"
echo 'PINCTRL_OBJECT_COMPILE_COMPLETE; FULL_IMAGE_AND_HARDWARE_UNTESTED'
