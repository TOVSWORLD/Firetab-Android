/* Isolated AArch64 PID 1 experiment. No libc, block-device or reboot interface. */
#include "cpu_contract.h"
typedef unsigned long usize;
static long call6(long n, long a, long b, long c, long d, long e, long f)
{
    register long x0 __asm__("x0") = a;
    register long x1 __asm__("x1") = b;
    register long x2 __asm__("x2") = c;
    register long x3 __asm__("x3") = d;
    register long x4 __asm__("x4") = e;
    register long x5 __asm__("x5") = f;
    register long x8 __asm__("x8") = n;
    __asm__ volatile("svc #0" : "+r"(x0) : "r"(x1), "r"(x2), "r"(x3),
                     "r"(x4), "r"(x5), "r"(x8) : "memory", "cc");
    return x0;
}
static long console = 1;
static usize length(const char *s) { usize n = 0; while (s[n]) ++n; return n; }
static void output(const char *s, usize n)
{
    while (n) {
        long r = call6(64, console, (long)s, n, 0, 0, 0);
        if (r == -4) continue; /* EINTR */
        if (r <= 0) return;
        s += r; n -= r;
    }
}
static void say(const char *s) { output(s, length(s)); }
static void dump(const char *path)
{
    char buffer[512];
    long fd = call6(56, -100, (long)path, 0, 0, 0, 0); /* openat, read-only */
    usize remaining = 16384;
    say("FILE "); say(path); say("\n");
    if (fd < 0) { say("UNAVAILABLE\n"); return; }
    while (remaining) {
        usize count = remaining < sizeof(buffer) ? remaining : sizeof(buffer);
        long n = call6(63, fd, (long)buffer, count, 0, 0, 0);
        if (n == -4) continue;
        if (n < 0) { say("READ_ERROR\n"); break; }
        if (!n) break;
        output(buffer, n); remaining -= n;
    }
    if (!remaining) say("\nREAD_LIMIT\n");
    call6(57, fd, 0, 0, 0, 0, 0);
    say("\nEND_FILE\n");
}
/* Private evidence stays in this buffer and is never passed to output(). */
static long read_private(const char *path, char *buffer)
{
    long fd = call6(56, -100, (long)path, 0, 0, 0, 0);
    usize used = 0;
    if (fd < 0) return -1;
    while (used < 4097) {
        long n = call6(63, fd, (long)(buffer+used), 4097-used, 0, 0, 0);
        if (n == -4) continue;
        if (n < 0) { used = 4097; break; }
        if (!n) break;
        used += n;
    }
    call6(57, fd, 0, 0, 0, 0, 0);
    return used > 4096 ? -1 : (long)used;
}
static void cpu_contract(void)
{
    char buffer[4097];
    const char *states[] = {"missing", "valid", "conflict", "duplicate", "malformed"};
    long n = read_private("/proc/cmdline", buffer);
    say("FIRETABS_CPU_CONTRACT_V1\nLIMIT_NR_CPUS=");
    say(n < 0 ? "unavailable" : states[parse_limit(buffer, n, "nr_cpus", "nr_cpus=1")]);
    say("\nLIMIT_MAXCPUS=");
    say(n < 0 ? "unavailable" : states[parse_limit(buffer, n, "maxcpus", "maxcpus=0")]);
    n = read_private("/sys/devices/system/cpu/online", buffer);
    int only = 0, count = n < 0 ? -1 : parse_online(buffer, n, &only);
    say("\nONLINE_CPUS=");
    if (count < 0) say("unavailable");
    else {
        char digits[5]; usize used = 0;
        do { digits[used++] = '0'+count%10; count /= 10; } while (count);
        while (used) output(digits+--used, 1);
    }
    say(only ? "\nONLINE_BOOT_CPU_ONLY=yes" : "\nONLINE_BOOT_CPU_ONLY=no");
    n = read_private("/sys/firmware/devicetree/base/psci/status", buffer);
    say("\nPSCI_DT_STATUS=");
    if (n < 0) say("unavailable");
    else if (equal_bytes(buffer, n, "disabled") || (n == 9 && buffer[8] == 0 && equal_bytes(buffer, 8, "disabled"))) say("disabled");
    else if ((n == 5 && buffer[4] == 0 && equal_bytes(buffer, 4, "okay")) || (n == 3 && buffer[2] == 0 && equal_bytes(buffer, 2, "ok"))) say("enabled");
    else say("unrecognized");
    say("\nFIRETABS_CPU_CONTRACT_END\n");
}
__attribute__((noreturn)) void _start(void)
{
    long fd = call6(56, -100, (long)"/dev/console", 257, 0, 0, 0);
    if (fd >= 0) console = fd;
    say("FIRETABS_DIAGNOSTIC_INIT_V1\n");
    /* Mount only kernel virtual filesystems. No devtmpfs or storage mounts. */
    long proc = call6(40, (long)"proc", (long)"/proc", (long)"proc", 15, 0, 0);
    long sys = call6(40, (long)"sysfs", (long)"/sys", (long)"sysfs", 15, 0, 0);
    say(proc == 0 ? "PROC_MOUNT_OK\n" : "PROC_MOUNT_FAILED\n");
    say(sys == 0 ? "SYSFS_MOUNT_OK\n" : "SYSFS_MOUNT_FAILED\n");
    dump("/proc/version");
    dump("/proc/meminfo");
    dump("/proc/iomem");
    dump("/proc/uptime");
    cpu_contract();
    say("FIRETABS_DIAGNOSTIC_IDLE\n");
    for (;;) {
        const long delay[2] = {60, 0};
        call6(101, (long)delay, 0, 0, 0, 0, 0);
    }
}
