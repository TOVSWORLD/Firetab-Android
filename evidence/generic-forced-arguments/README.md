# Executed generic forced-argument proof (#119)

CI run40279916842/job121430735801 passed at exact project revision
710edcfdfa7c3f003ededf8e40643fde4707bbb1 with ACK
d9318bdb4c34e8b2d997b4f67ced56b120b22b87. Total job23m47s; VM observation5.93s
including the required five-second idle endpoint. This is an executed kernel/
initramfs result, not merely a config-text or compile result.

The incoming QEMU args contained nr_cpus=4/maxcpus=3. Actual sanitized init
observations reported intended nr_cpus=1/maxcpus=0 valid, one online CPU and CPU0
alone. PSCI DT status was unavailable, so the separate primary-only contract
remains false. This proves the forced generic kernel argument mechanism under
these inputs; it does not establish the device loader's behavior or absence of
firmware calls on douglas.

The resolved config was reconstructed from timestamped CI output and its exact
SHA256 matches the run report. Rendered init verdicts were independently parsed
and match the final JSON. Original raw console digest is retained as reported by
the CI tester; the timestamped rendered job log does not reconstruct original
serial bytes, so no independent raw-console rehash is claimed. Full downloaded
job-log length/hash and CI link are recorded for provenance. Raw log stays ignored.

`runtime-result.json` retains exact config/Image/initramfs/console/source hashes,
command, measurements, timing and explicit false hardware/readiness flags.
`resolved.config` retains the exact hash-verified config. Compiled binary artifacts
are not archived in this repository; the hashes identify the executed outputs,
not a downloadable tablet firmware package. No tablet access, unlock, firmware
assembly/execution or flashing occurred.

Verify the retained consistency checks with
`python3 scripts/verify_generic_force_evidence.py`. These checks do not rerun
QEMU or authenticate GitHub independently. Tests reject changed config, missing
incoming conflict, bad observations and accidental hardware qualification.

Remaining: physical safe entry, required firmware arguments, memory ownership,
actual device console, restore compatibility and all hardware/Android/app gates.
Generic success closes119 only, not106/21/22 or a tablet test-readiness gate.
