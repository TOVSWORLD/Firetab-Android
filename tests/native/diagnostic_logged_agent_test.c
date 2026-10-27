/* Native host synthetic UART/frame arrays only, no physical or ARM execution. */
#include <assert.h>
#include <string.h>
#include "logged_agent.h"
static unsigned calls;
static int receive(void *p,uint8_t *q,size_t n) {
    (void)p;memset(q,0,n);memcpy(q,"FTDQ",4);q[4]=1;q[5]=1;q[8]=1;return (int)n;
}
static int send(void *p,const uint8_t *q,size_t n){(void)p;(void)q;return (int)n;}
static int call(void *p){calls++;if(p)((volatile uint32_t *)p)[5]=0;return 0;}
static int read_image(void *p,uint16_t o,uint16_t n,uint8_t *r){(void)p;(void)o;(void)n;(void)r;return -1;}
int main(void) {
    volatile uint32_t regs[6]={0};regs[5]=0x20;
    struct diagnostic_agent_io io={1,1,receive,send,call,read_image,0};struct diagnostic_log_result r;
    assert(diagnostic_logged_run(&io,regs,64,&r)==0 && calls==1 && r.logging_complete);
    assert(r.agent_invoked && r.agent_result==0 && r.entry_queued==11 && r.exit_queued==12);
    assert(diagnostic_logged_run(&io,regs,2,&r)==-1 && !r.agent_invoked && calls==1);
    io.version=0;
    assert(diagnostic_logged_run(&io,regs,64,&r)==0 && r.agent_invoked && r.agent_result==-1 && r.exit_queued==11);
    io.version=1;io.opaque=(void *)regs;
    assert(diagnostic_logged_run(&io,regs,64,&r)==-1 && r.agent_invoked && r.agent_result==0 && !r.logging_complete);
    assert(r.exit_queued==0);
    regs[3]=0x80;
    assert(diagnostic_logged_run(&io,regs,64,&r)==-1 && !r.agent_invoked);
    assert(diagnostic_logged_run(&io,0,64,&r)==-1 && !r.agent_invoked);
    return 0;
}
