/* Pure bounded parsers: never return or emit untrusted argument text. */
#ifndef FIRETABS_CPU_CONTRACT_H
#define FIRETABS_CPU_CONTRACT_H
enum limit_state { LIMIT_MISSING, LIMIT_VALID, LIMIT_CONFLICT, LIMIT_DUPLICATE, LIMIT_MALFORMED };
static int equal_bytes(const char *a, unsigned long n, const char *b)
{
    unsigned long i = 0;
    while (b[i]) { if (i >= n || a[i] != b[i]) return 0; ++i; }
    return i == n;
}
static enum limit_state parse_limit(const char *data, unsigned long n, const char *key, const char *wanted)
{
    unsigned long i = 0, count = 0;
    int valid = 0;
    if (!n || n > 4096) return LIMIT_MALFORMED;
    if (data[n-1] == '\n') --n;
    for (i = 0; i < n; ++i)
        if (data[i] < 32 || data[i] > 126 || data[i] == '"' || data[i] == '\'' || data[i] == '\\')
            return LIMIT_MALFORMED;
    i = 0;
    while (i < n) {
        unsigned long start, end, name;
        while (i < n && data[i] == ' ') ++i;
        start = i;
        while (i < n && data[i] != ' ') ++i;
        end = i; name = start;
        while (name < end && data[name] != '=') ++name;
        if (equal_bytes(data+start, name-start, key)) {
            ++count;
            valid = equal_bytes(data+start, end-start, wanted);
        }
    }
    if (count > 1) return LIMIT_DUPLICATE;
    if (!count) return LIMIT_MISSING;
    return valid ? LIMIT_VALID : LIMIT_CONFLICT;
}
static int parse_online(const char *data, unsigned long n, int *boot_only)
{
    unsigned long i = 0;
    int total = 0, previous = -1, first = -1;
    if (!n || n > 4096) return -1;
    if (data[n-1] == '\n') --n;
    if (!n) return -1;
    while (i < n) {
        int a = 0, b;
        if (data[i] < '0' || data[i] > '9') return -1;
        do { a = a*10+data[i++]-'0'; if (a >= 4096) return -1; }
        while (i < n && data[i] >= '0' && data[i] <= '9');
        b = a;
        if (i < n && data[i] == '-') {
            ++i; b = 0;
            if (i == n || data[i] < '0' || data[i] > '9') return -1;
            do { b = b*10+data[i++]-'0'; if (b >= 4096) return -1; }
            while (i < n && data[i] >= '0' && data[i] <= '9');
        }
        if (a <= previous || b < a) return -1;
        if (first < 0) first = a;
        total += b-a+1; previous = b;
        if (i < n && (data[i++] != ',' || i == n)) return -1;
    }
    *boot_only = total == 1 && first == 0;
    return total;
}
#endif
