#ifndef DIAGNOSTIC_DISPATCHER_H
#define DIAGNOSTIC_DISPATCHER_H
#include <stdint.h>
#include <stddef.h>
/* No transport/entry binding. Callers must zero-init a new context. */
struct diagnostic_context {
    uint32_t sequence;
    uint8_t called, failed, busy;
};
/* Callbacks are injected; no address or target pointer arrives on the wire. */
typedef int (*diagnostic_call)(void *opaque);
typedef int (*diagnostic_read)(void *opaque, uint16_t offset, uint16_t length, uint8_t *output);
int diagnostic_dispatch(struct diagnostic_context *context,
    const uint8_t *request, size_t request_bytes,
    uint8_t *response, size_t capacity, size_t *response_bytes,
    diagnostic_call call, diagnostic_read read, void *opaque);
#endif
