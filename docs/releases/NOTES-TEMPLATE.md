# PROJECT VERSION — CHANNEL

## Release identity

Project, tag, main release merge SHA, exact tested source revision, release issue and
manifest path. Explicitly state source snapshot vs firmware vs panel load.

## Scope and changes

Concrete user-visible changes and linked PRs. Separate Android/kernel/platform versions
from project version. Credit contributors and upstream work.

## Validation

List actual commands/tests, hardware variants, processor model/firmware where applicable,
toolchain/source pins, log hashes, duration and results. State what was not tested.

## Compatibility and limitations

Device codenames/partition layouts, ABI and platform requirements, supported functions,
known failures and security patch coverage including kernel/vendor/blob gaps.

## Install, upgrade and recovery

Link the exact reviewed owner procedure, data migration and rollback/recovery limits.
For source snapshots, state “No installable firmware or panel runtime is included.”

## Assets and provenance

Artifact names/bytes/SHA256, signatures, SBOM/component licenses, source links and
applicable source offer. Exclude packages without confirmed redistribution rights.

## Support

Named maintainer, channel, support start/end dates or explicit experimental status,
issue/support link and private security-report link. Do not call experimental work LTS.
