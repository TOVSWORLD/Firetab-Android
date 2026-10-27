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

## Supplied eMMC geometry decoder (#307)

`decode_offline_emmc_geometry.decode_geometry` accepts exactly 512 supplied
EXT_CSD bytes for reviewed revisions 6..8. It derives user bytes from little-endian
SEC_COUNT in 512-byte units, independently of the current 512/4096 data-sector
size, and both hardware boot regions from BOOT_MULT times 128KiB. Reviewed caps
are 64GiB user/32MiB per boot region. Zero/unsupported/malformed values fail.
The [primary source receipt](../../evidence/offline-emmc-geometry/sources.json)
records committed source hashes, definitions and kernel decoding ranges.

The decoder reports the supplied access bits and distinguishes ordinary user/
boot access from RPMB/other access. Project boot1/boot2 map to Linux boot0/boot1;
it sends no selector. Four synthetic tests cover capacities, 4096-sector unit
handling, RPMB classification and malformed fields; all 284 host tests pass.
No actual EXT_CSD was collected. Supplied values cannot prove device origin,
acknowledged selection, independent acquisition or restoration, and every such
qualification flag remains false. This supplies a future evidence decoder,
not a memory-read or collection procedure.

## Cross-checking supplied geometry against both sets (#309)

The two-set verifier now optionally accepts `--ext-csd supplied.bin`, a regular
host file limited to the exact 512 bytes required by the decoder. Both manifest
sector sizes and all three expected region lengths must match the supplied
geometry before file verification. Thus two internally consistent copies with
the same wrong extent no longer pass this optional check. Without metadata,
the existing two-set integrity mode remains available and reports no geometry
cross-check. Output never publishes the raw EXT_CSD or identifiers.

Three additional synthetic tests cover matching geometry without origin claims,
wrong user/boot capacity despite matching copies, sector mismatch and malformed
metadata; all 287 host tests pass. Supplied geometry consistency is not device
origin, fresh acquisition, acknowledged region selection or independent reads.
No metadata was collected or selector/transport bound. Original-state acquisition,
RTC/RPMB state and reachable post-failure restoration remain open.

## Write protection and selection are separate restore prerequisites (#315)

The cached kernel revision's [source receipt](../../evidence/restore-write-protection/report.json)
separates three states that matching dump files cannot establish. This source has
not been matched to the installed binary; none of these states was acquired.

- `force_ro_store` changes the host disk read-only flag, still honoring the driver's
  `read_only` value. It does not clear card boot write protection. A host flag
  observation therefore cannot establish card-level writable restore.
- Card boot protection comes from EXT_CSD BOOT_WP. The separate power-lock path
  sets power protection using a card switch, changes cached/host state only on
  success, and logs failure while still returning the input byte count. A successful
  sysfs write count alone would not prove that card operation succeeded. Its show
  path uses cached flags, not a fresh card read. Permanent and power protection
  are distinguished in source; no operation to alter either is proposed here.
- The block partition switch preserves the other configuration bits and updates
  cached selection after reported switch success, without independent readback
  in this function. Initialization's default-user switch explicitly tolerates
  EBADMSG. Neither cached selection nor a filename establishes actual selected
  region or successful restoration.

A future qualified restore route needs evidence of original card configuration,
actual protection/selection, error propagation, exact region extents, readback and
reachability after failure. Power-cycle behavior, security/rollback state and
original RTC/RPMB remain separate. This is source analysis, not instructions to
change sysfs, card state or power. Existing offline geometry verification is
unchanged and intentionally does not claim writable restore.
