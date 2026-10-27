# Offline recovery escrow verification

This host-only tool validates already collected regular files. It does not collect
backups, contact the tablet, load firmware or restore anything. #106 remains open.
Entry/bootstrap, actual region selection, security-state preservation, restore
compatibility and physical logging require separate evidence.

Run `python3 scripts/verify_offline_escrow.py /absolute/private/manifest.json`.
Keep the manifest, images and output under ignored `out/` or another private
location. Use this private JSON structure with actual independently established
region sizes and expected SHA256 values (placeholders below are not valid inputs):

```json
{
  "logical_sector_bytes": 512,
  "regions": {
    "user": {"file": "user.bin", "expected_bytes": 0, "sha256": "REPLACE"},
    "boot1": {"file": "boot1.bin", "expected_bytes": 0, "sha256": "REPLACE"},
    "boot2": {"file": "boot2.bin", "expected_bytes": 0, "sha256": "REPLACE"}
  }
}
```

File paths resolve relative to the manifest. The tool rejects symlinks,
nonregular files, repeated paths/inodes, missing regions, unexpected record
fields, wrong lengths and wrong digests. It streams hashes and caps each GPT
entry array at 4 MiB; no dependency installation, download or paid resource is
required. A full user-region image entails reading its full length locally.
Never substitute the tablet's displayed usable filesystem capacity for measured
raw user-region geometry. Boot region sizes are not inferred from filenames.

For the user-region image, it reads GPT headers at LBA1 and the final LBA,
validates each header and its own entry-array CRC, checks reciprocal locations,
matching disk geometry/GUID/table contents, metadata boundaries, nonzero unique
partition GUIDs, usable-range limits and partition overlap. Both 512-byte and
4096-byte logical sectors are supported. Layout and CRC definitions follow
[UEFI 2.11 chapter5](https://uefi.org/specs/UEFI/2.11/05_GUID_Partition_Table_Format.html).
This is a strict recovery-integrity subset, not a full UEFI conformance validator;
protective MBR semantics, filesystem contents and firmware signatures are outside
its scope. Unsupported or inconsistent layouts fail closed for this purpose.

Exit0 means offline file checks passed. The JSON still sets
`collection_region_identity_verified`, `restore_qualified` and
`physical_test_ready` to false. A checksum supplied by the same faulty collector
only confirms that file's bytes; it cannot establish where they came from. Two
GPT locations in one image do not prove independent acquisition sessions. A
copied primary header at the secondary location fails the location checks.
RPMB keys/counters/fuses and rollback policy are not reconstructible from these
three files. No successful output establishes a recoverable loading route.

Output omits paths, GUIDs, partition names and image contents; failures emit only
an exception category and false qualification flags. Treat any actual private
backup as sensitive regardless of this output policy. Regular-file checks and
change detection assume a trusted local directory, not hostile concurrent file
replacement.

Tests use generated host fixtures only:
`python3 -m unittest discover -s tests -q`. They cover both sector sizes,
primary/secondary/table corruption, copied primary header, rechecksummed invalid
geometry and inconsistent copies, partition overlap, truncation/digest mismatch,
symlink/nonregular rejection, and sanitized CLI success/failure. No tablet backup
has been collected or validated with this tool.

## Cached official components versus original-state coverage (#303)

The build-checked cached OTA index for `50.6.5.9_user_659664620` lists boot,
preloader, LK, preloader header and update/system assets. A bounded inventory
rehashes the cached components and index receipt in
[official restore coverage](../../evidence/official-restore-coverage/report.json).
No full package was downloaded or signature verification newly established.
This index is not a manifest of original hardware-region captures from the tablet.

A packaged preloader plus header assets is not proof of the complete original
first boot region. Packaged LK/boot do not supply original user-region bytes or
both boot regions. In particular, the previously traced second-boot record
container has no acquired original device contents in current evidence; generic
components cannot establish that record's preservation or restoration. RTC
state, RPMB/security state and a restore mechanism reachable after failure are
also separate from these component files. No claim is made that other packages
cannot contain additional material; this is the coverage of the inspected cache.

Therefore retain these components as provenance/build references, not a completed
recovery escrow. Before any physical proposal, require independently consistent
original region evidence, provenance/geometry validation and a separately
qualified restoration path for the specific intended changes. No device read,
flash, register operation or helper execution occurred in this inventory.

## Two-set consistency check (#305)

`compare_offline_escrow.py first.json second.json` verifies two explicitly supplied
host-file manifests using the existing length/SHA256/GPT checks. It requires all
six region files to have distinct host inode identities, checks file metadata
around validation and requires matching logical geometry, lengths and digests
for corresponding regions. Shared hardlinks/symlinks, changed files, corrupt GPT
or individually valid but disagreeing captures fail. Output excludes paths,
GUIDs, partition names and identifier data.

Four synthetic tests cover agreement without provenance claims, cross-set
hardlinks, differing bytes with valid individual hashes, corrupt GPT and symlinks.
Agreement is necessary consistency evidence, not proof that two actual device
acquisitions occurred: copies can use separate inodes. Region origin, original
state, RTC/RPMB, independent transport and a post-failure restore mechanism remain
unverified. The checker never acquires data or accesses a device; only tiny
synthetic host files were used for development.

Before eventual owner evidence collection, define acquisition provenance and
acknowledged hardware-region selection separately. Do not use this checker to
turn official component copies into original-state escrow or to authorize writes.
