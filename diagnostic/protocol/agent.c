/* Owned callable protocol loop; no boot entry, USB or physical address binding. */
#include "agent.h"
int diagnostic_agent_run(const struct diagnostic_agent_io *io) {
    struct diagnostic_context context;
    uint8_t request[16],response[272];
    size_t written;
    uint32_t i;
    if (!io || io->version!=1 || !io->transactions || io->transactions>16 ||
        !io->receive || !io->send || !io->call || !io->read) return -1;
    context.sequence=0;context.called=0;context.failed=0;context.busy=0;
    for(i=0;i<io->transactions;i++) {
        if(io->receive(io->opaque,request,sizeof(request))!=(int)sizeof(request)) return -1;
        if(diagnostic_dispatch(&context,request,sizeof(request),response,sizeof(response),
                               &written,io->call,io->read,io->opaque)!=0) return -1;
        if(io->send(io->opaque,response,written)!=(int)written) return -1;
    }
    return 0;
}
