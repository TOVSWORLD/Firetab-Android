# Current status and known limitations

Neither project has a current-kernel firmware build, boot result or validated installable
release. There is no supported installation/upgrade/rollback procedure for project
firmware yet. Existing third-party ROMs are external reference work, not our releases.

- An initial Android 17 / 6.18 ACK candidate and source support matrix are documented
  in development/DOUGLAS-KERNEL-AUDIT.md. Kernel integration, compilation and the full
  peripheral inventory remain outstanding.
- An experimental douglas DTB now compiles and is inspected in CI; its inherited
  memory/PSCI assumptions and full binding validation remain unresolved.
- Android 17 platform integration, graphics/media interfaces, enforcing SELinux and
  real memory/storage behavior are unvalidated.
- Google Play/services distribution and device certification are not established.
- Panel-mode selector, client execution and CP4 integration have not been implemented
  or physically tested by this project.
- Native Crestron services/libraries are missing from the inspected APKs. Public package
  inspection does not establish complete dependencies, licensing or runtime portability.
- The historical Dockerfile is unbuilt and does not provision a pinned Android 17 toolchain.
- Current inspection host is macOS ARM64 on a case-insensitive filesystem; it is not
  the proposed full Android build host. See CONTINUE.md for resource requirements.

Use each project's `validation.json` for measured stage results, with exact commits and
hashes. Statements about a physically absent feature differ from an existing component
that lacks a driver. Do not report either as “supported” without appropriate evidence.
