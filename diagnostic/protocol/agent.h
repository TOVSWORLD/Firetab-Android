#ifndef DIAGNOSTIC_AGENT_H
#define DIAGNOSTIC_AGENT_H
#include "dispatcher.h"
/* Injected ABI, never populated from wire bytes. All callbacks must be bounded. */
struct diagnostic_agent_io {
    uint32_t version;
    uint32_t transactions;
    int (*receive)(void *opaque, uint8_t *output, size_t length);
    int (*send)(void *opaque, const uint8_t *input, size_t length);
    diagnostic_call call;
    diagnostic_read read;
    void *opaque;
};
int diagnostic_agent_run(const struct diagnostic_agent_io *io);
#endif
