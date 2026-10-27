/* Owned callable protocol loop; no boot entry, USB or physical address binding. */
#include "agent.h"
int diagnostic_agent_run(const struct diagnostic_agent_io *io) {
    struct diagnostic_context context;
    uint8_t request[16],response[272];
    size_t written;
    uint32_t i, transactions;
    int (*receive)(void *,uint8_t *,size_t);
    int (*send)(void *,const uint8_t *,size_t);
    diagnostic_call call;
    diagnostic_read read;
    void *opaque;
    if (!io || io->version!=1 || !io->transactions || io->transactions>16 ||
        !io->receive || !io->send || !io->call || !io->read) return -1;
    /* Freeze the validated ABI before callbacks can modify caller storage. */
    transactions=io->transactions;receive=io->receive;send=io->send;
    call=io->call;read=io->read;opaque=io->opaque;
    context.sequence=0;context.called=0;context.failed=0;context.busy=0;
    for(i=0;i<transactions;i++) {
        if(receive(opaque,request,sizeof(request))!=(int)sizeof(request)) return -1;
        if(diagnostic_dispatch(&context,request,sizeof(request),response,sizeof(response),
                               &written,call,read,opaque)!=0) return -1;
        if(send(opaque,response,written)!=(int)written) return -1;
    }
    return 0;
}
