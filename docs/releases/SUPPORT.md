# Support, security updates and LTS

No product release or LTS branch is currently supported. Android major versions,
LineageOS version numbers, Linux LTS branches and this project's support periods are
separate concepts. No arbitrary Android release becomes “LTS” through our naming.

Before declaring stable or LTS, publish a support record naming project/device variant,
Android and kernel branches, covered components, named maintainer, start and end dates,
update channel, test matrix and capacity. A stable product targets at least 12 months
of maintenance; an LTS designation requires an explicit at-least-24-month commitment.
These are acceptance conditions for a future declaration, not commitments active today.
If capacity is unavailable, keep the stream experimental and say so.

Review upstream Android/kernel security changes monthly. For supported streams, target
triage within seven days of a relevant public bulletin and a tested update in the next
monthly window; confirmed urgent exposure may use an out-of-cycle patch. These are
best-effort targets, not SLAs or a claim that proprietary blob vulnerabilities are fixed.
Record actual coverage and any unsupported upstream component. Never increase an Android
security patch level string beyond the changes actually integrated and validated.

Publish an end-of-support notice at least 90 days before a planned end where possible,
with last supported release, unresolved security gaps and migration/recovery options.
Unexpected upstream or maintainer loss may shorten support; disclose it promptly and
stop recommending unsupported builds. Do not silently delete old release evidence.

While pre-release, assess upstream changes and maintain transparent limitations, without
promising stable security coverage or compatibility with every future app update.
