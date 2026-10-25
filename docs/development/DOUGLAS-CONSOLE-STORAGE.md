# Douglas console/storage reuse — issue #22

The clock+pinctrl [Image run](https://github.com/TOVSWORLD/Firetab-Android/actions/runs/40170429213)
already compiled ACK's `8250_mtk.o` and `mtk-sd.o`. Captured compiler excerpts,
resolved configuration, source/binding files and hashes are in
[evidence/console-storage](../../evidence/console-storage). No additional driver
implementation is justified merely to duplicate this compile result.

## Console

The captured SoC DT declares UART0 at 0x11002000 with fallback
`mediatek,mt6577-uart`, named baud/bus clocks and TX/RX DMA references. The common
Amazon DT enables UART0, selects its pins and names serial0 as stdout at 921600.
ACK's driver matches this fallback and registers an OF early console; both
SERIAL_8250_MT6577 and SERIAL_8250_CONSOLE are built in. Baud/bus clock lookups
match the captured names. Runtime initialization writes UART registers, so a
compiled console is not a verified working log channel.

Physical pad access, signal voltage, loader UART policy and actual output are
unknown. Do not assume the USB charging connector exposes this UART. The donor
DMA dependencies and whether polling-only operation is appropriate require
further review; no property is removed merely to avoid a deferred dependency.

## MMC

The SoC DT uses `mediatek,mt8163-mmc`, `mediatek,mt2701-mmc`; ACK matches the
second string. The source/hclk clocks required by the driver and optional
bus_clk name are supplied in the donor node. Name agreement does not establish
correct parent rates or controller-register compatibility. The donor eMMC board
node enables 8-bit, 200 MHz/HS200 operation with specific PMIC supplies. Those
voltages/timings and clock assignments are not physically validated here.

The MMC_MTK and MMC_BLOCK drivers are built in and were actually compiled during
the successful full Image run. Neither eMMC nor SD has been probed on douglas.
No partitions, filesystem mounts, data integrity or safe recovery are validated.
A first diagnostic initramfs should avoid depending on internal storage; any
controller-initialization policy must be decided as part of the qualified test
configuration, not inferred from successful compilation.

## Binding and readiness gaps

Pinned ACK's mediatek,uart.yaml and mtk-sd.yaml do not list MT8163. Their actual
compatible constraints therefore require adaptation/validation for the donor
nodes (#27); the presence of a driver fallback is not a schema pass. Captured
binding files alone are not a complete matching schema corpus.

Keep #22 open for full board/provider/schema integration, legacy wiring/timing
review, a usable log channel and later authorized hardware evidence. Coordinate
firmware/memory/image/recovery contract #21 and power providers #20. No physical
access or test image is requested by this source-review milestone.
