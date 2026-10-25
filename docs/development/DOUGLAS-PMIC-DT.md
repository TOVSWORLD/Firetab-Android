# PMIC child-name candidate — issue #27

This narrow structural patch renames mt6323regulator to regulators, mt6323keys
to keys, and mt6397codec to audio-codec, matching pinned ACK's
[MT6397/MT6323 MFD binding](../../evidence/pmic-dt/ack/Documentation/devicetree/bindings/mfd/mediatek,mt6397.yaml).
Labels and compatible strings remain intact; register/voltage/supply properties
are unchanged. ACK's MFD cells match by compatible; this is not a claim of
successful regulator/audio/key probe on hardware.

Baseline experiment remains unchanged. The separate candidate is pinned in
projects/firetabs-android/kernel/dtb/pmic-node-names.json, with three patch hashes
and expected DTB size/hash. Reproduce after the ordinary DT tooling setup:

```sh
python3 scripts/build_douglas_dtb.py
python3 scripts/build_douglas_dtb.py --experiment pmic-node-names
python3 scripts/compare_pmic_dtb.py
python3 scripts/validate_douglas_bindings.py --experiment pmic-node-names
```

The final command still exits **1** because schema validation has not passed.
Candidate DTB: 26,275 bytes, SHA256
119b6666a3caf217675d5aead3e9b0e0b21287d3e21f9d36e7d047f26698eddf.
Actual binary comparison covers 186 nodes/880 property values, allowing only the
three child-path substitutions (including regulator descendants). Every property
value, including memory, supplies, voltages and phandles, matches baseline.
CI repeats both DT compilations and the comparison; no firmware image is packed.

Recorded full-context diagnostics drop from 36 to 34 validation errors, with 61
unmatched entries still present. The structured signature delta removes two MFD
parent diagnostics and adds none. The unrelated upstream Gunyah YAML parse error
also remains; no schema/hardware pass is claimed. Logs/results are under
[evidence/pmic-dt](../../evidence/pmic-dt).

The separate '#power-domain-cells' diagnostic is deliberately unresolved. Pinned
ACK's mt6323-poweroff.c registers a system power-off handler, not a generic PM
domain provider. Adding domain cells solely for a schema count would assert an
interface the reviewed driver does not implement. Review the binding selection
and intended node semantics before changing that property. The earlier missing-
cell diagnostic should not be interpreted as proof of a missing hardware domain.
