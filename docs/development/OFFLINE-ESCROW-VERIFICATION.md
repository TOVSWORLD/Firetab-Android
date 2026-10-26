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
