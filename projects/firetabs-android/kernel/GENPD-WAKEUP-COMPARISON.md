# Pinned genpd wakeup comparison — #20

The missing modern implementation is now acquired. The selected ACK revision
`d9318bdb4c34e8b2d997b4f67ced56b120b22b87` uses `drivers/pmdomain/core.c`;
the old `drivers/base/power/domain.c` URL returns404. Exact official source URLs,
hashes and the legacy Git object are retained in `evidence/power-port/wakeup-core`.

Legacy `scpsys_active_wakeup` returns domain data; all eight reviewed legacy
MT8163 domains set it true. The selected modern driver sets
`GENPD_FLAG_ACTIVE_WAKEUP` only for `MTK_SCPD_ACTIVE_WAKEUP`; candidate descriptors
omit that capability. This is an actual source policy difference.

Legacy noirq returns early for `suspend_power_off || (wakeup_path && active)`.
Modern noirq first calls the generic suspend callback, then returns early for
`device_awake_path && active_flag && !device_out_band_wakeup`. The pinned header
resolves awake-path to the device wakeup-path Boolean and out-of-band to its
separate flag under CONFIG_PM_SLEEP. The16-row report compares those predicates.
With legacy already-off false and modern out-of-band false, equal active policy
produces equal wakeup early-return decisions. That limited result does not prove
whole suspend equivalence.

Legacy prepare may call `pm_runtime_resume` through `resume_needed`; modern
prepare delegates `pm_generic_prepare` with prepared-count handling. Generic
noirq callback ordering, locking, stop/start, counts and errors also differ. A
flag change cannot by itself restore identical behavior. Neither implementation
has been exercised on this device in this work.

Reproduce source hashes/anchors and finite branch table:

```sh
python3 scripts/validate_genpd_wakeup_comparison.py
```

No capability, driver or DT change is made. Next acceptance is the intended modern
device wakeup configuration and power-transition behavior before changing policy.
Runtime suspend/resume, DMA and independent failed-boot return remain unqualified.
