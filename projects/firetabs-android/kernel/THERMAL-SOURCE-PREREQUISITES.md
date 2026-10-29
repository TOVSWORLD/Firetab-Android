# MT8163 thermal source prerequisites (#27)

No thermal variant or binding is admitted by this finite source comparison.
The current ACK driver has no MT8163 OF match. The pinned MT8163 donor adds a
three-bank/three-sensor/channel11/coefficient165/V1 descriptor, but also globally
changes the callback/private-data and registration contract for existing SoCs.
Copying that whole change would alter existing aggregate reporting.

`python3 scripts/audit_thermal_source.py --check` compiles the actual selected
C functions under ASan/UBSan with RAM-only calibration, lock, temperature and
register-slot callbacks. No kernel, temperature, ADC or device operation runs.
The receipt locks exact ACK, donor, legacy thermal and legacy devinfo sources.

The actual ACK callback aggregates all banks and receives the thermal-controller
pointer. The donor callback receives one bank and reports only it; its probe
registers every bank rather than only ID0. With three synthetic distinct bank
temperatures, the compiled callbacks yield aggregate30000 versus bank0=10000,
bank1=20000, bank2=30000. These are test values, not measured temperatures.
Any eventual MT8163 per-bank support must isolate this boundary and preserve
all existing SoC behavior; candidate zones refer to IDs0/1/2.

Active legacy mux writes, captured by the actual C functions into virtual slots:

- Bank0: mux0,1.
- Bank1: mux2,16.
- Bank2: mux3,1,2,16.

Donor descriptor/mux arrays select bank0=0,1; bank1=1; bank2=0,1,2. The arrays
therefore are not equivalent to those active legacy writes. Nearby legacy
comments disagree with several active paths; comments alone cannot settle the
mapping. Neither source is an observed installed hardware oracle.

Legacy `thermal_cal_prepare` reads devinfo indices8/7/9 into temp0/1/2; devinfo
copies a chosen-node `atag,devinfo` array. Candidate nvmem declares12 bytes at
efuse offset0x100. The cached legacy kernel does not establish their identity.
Comments mentioning efuse0x180/184/188 are not executed MMIO mapping evidence;
this audit does not claim the candidate offset is wrong or replace it.

Given the same synthetic ordered words7/8/9, the compiled legacy and V1 parsers
agree on the first three VTS fields, ADC_GE and DEGC fields. Signed slope differs
in126 of256 ID/sign/slope cases: legacy forces slope0 when ID=0, whereas V1 uses
the positive field. This comparison is not whole conversion equivalence. Legacy
also decodes ADC_OE and normalizes ADC_GE for later conversion; the donor selects
existing V1 conversion unchanged. Actual calibration format/normalization,
coefficient/conversion and invalid-data policy need a justified MT8163 contract.
No security or thermal protection is relaxed to bypass this prerequisite.

The modern probe maps the thermal resource, obtains calibration before enabling
clocks, parses AUXADC/APMIXED phandles, resets optionally and enables both clocks
before buffer/bank programming. Candidate IRQ78 presence does not prove IRQ use:
the selected modern probe has no request_irq path. Resource bounds and actual
MMIO/clock/reset/calibration ownership remain source/runtime prerequisites.
Missing calibration may fall back to defaults in existing generic code; that
behavior is not independent proof of calibrated or safe MT8163 readings.

Next thermal acceptance needs source-backed word lineage and an explicit
variant-specific sensor/bank/calibration/conversion contract, then isolated C
implementation/negative tests and a new exact-head Image build before matching
metadata. Do not guess an MT8173 alias or globally change reporting. Full binding
contexts stay32/26 diagnostics, failed; DTBs and safety thresholds are unchanged.
Independent existing unmatched display-PHY source work can proceed while this
thermal prerequisite is unresolved. No owner hardware action is requested here.
