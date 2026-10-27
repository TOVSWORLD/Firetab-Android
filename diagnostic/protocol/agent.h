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
#if defined(__arm__)
_Static_assert(sizeof(struct diagnostic_agent_io)==28, "Embedded ARM32 IO ABI size");
_Static_assert(offsetof(struct diagnostic_agent_io,receive)==8, "Embedded callback offset");
_Static_assert(offsetof(struct diagnostic_agent_io,opaque)==24, "Embedded opaque offset");
#endif
int diagnostic_agent_run(const struct diagnostic_agent_io *io);
#endif
