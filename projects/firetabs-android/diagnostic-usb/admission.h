/* Unqualified runtime gates. No command-line or archive token may enable them. */
#ifndef FIRETABS_ACM_ADMISSION_H
#define FIRETABS_ACM_ADMISSION_H
#define FT_LOADING_QUALIFIED 0
#define FT_RETURN_QUALIFIED 0
#define FT_LOG_RETENTION_QUALIFIED 0
#define FT_DEVICE_ROLE_QUALIFIED 0
#define FT_SECURITY_POLICY_QUALIFIED 0
#define FT_IMMUTABLE_NAMESPACE_QUALIFIED 0
#define FT_DESCRIPTOR_ASSIGNMENT_QUALIFIED 0
/* No physical VID/PID assigned. Empty values fail identity checks if reached. */
#define FT_PHYSICAL_VID ""
#define FT_PHYSICAL_PID ""
#endif
