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


## Why the shutdown node selects a domain schema

The diagnostic names the generic
[power-domain.yaml](../../evidence/pmic-dt/ack/Documentation/devicetree/bindings/power/power-domain.yaml),
not the MT6323 MFD child definition. The generic schema's `$nodename` pattern
matches `power-controller` and its required list demands `#power-domain-cells`.
The MFD schema independently names this shutdown child `power-controller` and
permits the zero-cell property, but does not require it. This is a verified
selection overlap in the pinned corpus, rather than evidence that the shutdown
driver supplies PM domains.

The [MFD core](../../evidence/pmic-dt/ack/drivers/mfd/mt6397-core.c)
`mt6323_devs` entry supplies the shutdown driver's memory resource and matches
`mediatek,mt6323-pwrc`. The
[shutdown driver](../../evidence/pmic-dt/ack/drivers/power/reset/mt6323-poweroff.c)
uses that resource for PMIC BBPU accesses and registers a system-off handler.
Its reviewed implementation does not register a generic domain provider. Thus
absence of a DT `reg` property on this child is also not, by itself, proof that
its required resource is missing: the parent supplies it.

Resolution remains open in #27: reconcile the generic selector and MFD binding
with upstream binding maintainers, preserving the real shutdown interface.
Renaming this child alone would conflict with the existing parent binding;
adding domain cells merely to reduce the error count would not implement genpd.
No schema override, node rename, diagnostic suppression or DT property change
is made by this classification. The recorded result stays 34 errors and 61
unmatched entries, with the separate upstream YAML parse failure unresolved.
