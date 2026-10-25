# User-run stock information collection — issue #37

This tool is ready for a **read-only information-gathering session**, not a
firmware boot test. It has only been tested using fake device responses; no real
ADB/device collection has run. The actual firmware/memory evidence remains #21.

## Connection preparation

Confirm which computer will be used and a micro-USB **data** cable (plus a USB
adapter if needed). Amazon's [connection guide](https://developer.amazon.com/docs/fire-tablets/connecting-adb-to-device.html)
documents Fire tablet ADB connections. The shared Mac already has SDK Platform
Tools installed at `$HOME/Library/Android/sdk/platform-tools/adb`; host-only
`adb version` reports 36.0.2-14143358. No new download is needed on that Mac.
Other computers may require their own official Platform Tools/Windows driver.

USB debugging and computer authorization are prerequisites for collection.
Enabling debugging or accepting a computer key is a tablet setup change, separate
from the collector's read-only queries. Do not change these settings under the
current no-tablet-modification instruction; agree that setup step with the user
first. The agent must not initiate device queries merely because USB is attached.

## Reviewed collection scope

`scripts/collect_stock_facts.py` requires an explicit device serial and stops
unless manufacturer/model/device properties identify Amazon douglas/KFDOWI.
It uses fixed getprop/uname/cat/ls queries for software identity, kernel version,
RAM/iomem/partition metadata and individual readable DT root/memory properties.
It does not read raw partitions, full bootargs/serial DT blobs, household app
settings or logs. Kernel cmdline is retained only through a public boot-contract
key allowlist; the device serial and arbitrary stderr are not saved.

Each host command has a 15-second timeout and a 1 MiB limit per output pipe,
with process termination on overflow. At most eight validated memory-node names
are queried, with any limitation recorded. Permission-denied/absent DT properties
remain unavailable. It never escalates privileges, roots, reboots, mounts, writes
tablet settings, installs apps or flashes firmware. ADB itself can start its host
server; it is not a generic guarantee of zero background OS activity.

After the user approves connection/debugging setup and the read-only collection,
select the device locally using the official ADB listing. Do not post its serial
in a public issue. The user-run command from this repository is:

```sh
python3 scripts/collect_stock_facts.py \
  --adb "$HOME/Library/Android/sdk/platform-tools/adb" \
  --serial DEVICE_SERIAL
```

The placeholder must be replaced with the one selected serial. Reports are
written locally under ignored out/stock-facts with a timestamp. They contain
availability/exit status per field; missing data is not a successful firmware
identification or memory-handoff validation. Review the JSON before sharing it
in this conversation. Do not publish stock firmware or raw private device data.

Tests use only an injected fake transport, plus bounded-output/timeout checks
against a harmless local Python child process. CI never calls a real ADB binary.
The collector does not establish recovery, loader compatibility or a safe boot
procedure. A diagnostic firmware package still requires that separate work.
