/* Native host synthetic framing tests. No target instruction execution or device I/O. */
#include <assert.h>
#include <string.h>
#include "agent.h"
struct fixture { unsigned receive_count,send_count,calls;int short_receive,short_send; };
static int receive(void *p,uint8_t *q,size_t n) {
    struct fixture *f=p;unsigned sequence=++f->receive_count;
    assert(n==16);memset(q,0,n);memcpy(q,"FTDQ",4);q[4]=1;
    q[5]=(uint8_t)(sequence==1?1:2);q[8]=(uint8_t)sequence;
    if(sequence>1)q[14]=4;
    return f->short_receive?15:16;
}
static int send(void *p,const uint8_t *r,size_t n) {
    struct fixture *f=p;f->send_count++;
    assert(memcmp(r,"FTDR",4)==0 && n==(f->send_count==1?16:20));
    return f->short_send?(int)n-1:(int)n;
}
static int call(void *p) { ((struct fixture *)p)->calls++;return 0; }
static int read_image(void *p,uint16_t offset,uint16_t n,uint8_t *r) {
    (void)p;(void)offset;memset(r,0,n);return n;
}
int main(void) {
    struct fixture f={0};
    struct diagnostic_agent_io io={1,6,receive,send,call,read_image,&f};
    assert(diagnostic_agent_run(&io)==0 && f.receive_count==6 && f.send_count==6 && f.calls==1);
    memset(&f,0,sizeof(f));f.short_receive=1;
    assert(diagnostic_agent_run(&io)==-1 && f.calls==0 && f.send_count==0 && f.receive_count==1);
    memset(&f,0,sizeof(f));f.short_send=1;
    assert(diagnostic_agent_run(&io)==-1 && f.calls==1 && f.send_count==1 && f.receive_count==1);
    memset(&f,0,sizeof(f));io.transactions=17;
    assert(diagnostic_agent_run(&io)==-1 && f.receive_count==0);
    io.transactions=1;io.version=0;
    assert(diagnostic_agent_run(&io)==-1 && f.receive_count==0);
    return 0;
}
