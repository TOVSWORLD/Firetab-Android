# Source-matched MT8163 MIPI metadata (#27)

PR430 merged9c3f4a81c8fb791ee76b1266f0365177223ceb82 after all six exact-head
checks atb5e12688ced84a917657d928365dec969eb66a1c, including actual Linux run
40859970271. Three real PHY translation units, resolved builtin dependencies,
and final post-MIPI28645888-byte Image passed. The exact source/object/config/
vmlinux/Image receipt is evidence/mipi-kernel-integration/build-result.json.
It excludes earlier staged Image/gzip from MIPI acceptance and identifies W1
object hashes as pre-Image probes. No QEMU or physical PHY behavior was tested.

The opt-in `mt8163-mipi-tx` schema adds one exact compatible, requires one reset
and forbids unqualified nvmem/drive overrides. Existing SoCs retain their previous
reset prohibition and override policies. The standalone MT8163 branch preserves
older fallback branches; removing the new branch/property/conditional restores
the old schema structure exactly. No DT or driver changes in this scope.

35 actual decoded-node controls exercise required properties, cardinality/type
errors, zero clock/PHY argument widths, unreviewed fallback strings, forbidden
MT8163 overrides and preserved old-device behavior. The processed PHY schema
alone omits some implicit primitive type checks. The retained pipeline combines
it with relevant always/type selectors, proven equivalent to the full matched
validator for every frozen control. A valid drive control uses the decoded units
array[4000]; policy rejection is not confused with a scalar-type error.
52 relevant selectors/54 closed schemas retain that pipeline in portable form.

```
work/dtb-tool/venv/bin/python evidence/mipi-binding/check-controls.py --check
python3 scripts/validate_mipi_dependencies.py --dtb work/dtb-compile/pwrap-pmic-node-name/douglas.dtb
```

The separate fresh-DTB guard checks the actual disabled PHY resource4KiB against
the compiled0x6c minimum, APMIXED reference provider at0x1000c000/ID13, the fixed
clk26m declaration, INFRACFG reset provider/ID10 and disabled DSI PHY/PLL consumer
lineage. Source headers/tables/build scripts and accepted source output hashes
are locked. Source mapping is not physical reset delivery or a measured26MHz
clock. Other DSI engine/digital clock function and the controller driver remain
independently unqualified; this guard only qualifies the reviewed MIPI edges.

Full5186-YAML registered wrappers are reproduced by canonical-command.json and
isolated-command.json. Canonical32→31 (19unmatched/12validation), isolated26→25
(16/9): only the MIPI unmatched diagnostic disappears, no additions. Both wrappers
exit1/`passed:false`; Gunyah warning and disabled unmatched MT8163 AFE child remain.
The canonical/isolated DTB bytes and all disabled states are unchanged.

Schema cardinality, board/source graph metadata, generic compilation and physical
PLL/analog/reset/clock/lane/panel behavior are separate. No display/PHY enable,
helper/firmware/device/reset/electrical operation or runtime recovery/log gate is
admitted. Next independent source prerequisite is the disabled MT8163 DSI
controller's actual match/variant/IRQ/clock/power/resource/probe ownership.
