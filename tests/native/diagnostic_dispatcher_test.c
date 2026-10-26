/* Native host test: synthetic arrays/callbacks only, never ARM firmware execution. */
#include <assert.h>
#include <string.h>
#include "dispatcher.h"
static unsigned calls;
static uint8_t image[1080];
static int call(void *opaque) {
    (void)opaque; calls++; image[48]=0x31; return 0;
}
static int read_image(void *opaque,uint16_t offset,uint16_t n,uint8_t *out) {
    (void)opaque; memcpy(out,image+offset,n); return n;
}
static int short_read(void *opaque,uint16_t o,uint16_t n,uint8_t *out) {
    (void)opaque;(void)o;(void)n;(void)out; return 0;
}
static void request(uint8_t *q,unsigned op,unsigned sequence,unsigned offset,unsigned n) {
    memset(q,0,16);memcpy(q,"FTDQ",4);q[4]=1;q[5]=(uint8_t)op;q[8]=(uint8_t)sequence;
    q[12]=(uint8_t)offset;q[13]=(uint8_t)(offset>>8);q[14]=(uint8_t)n;q[15]=(uint8_t)(n>>8);
}
int main(void) {
    struct diagnostic_context c={0}; uint8_t q[16],r[272];size_t n=99;unsigned offset,seq=1;
    request(q,1,seq,0,0);
    assert(diagnostic_dispatch(&c,q,16,r,sizeof(r),&n,call,read_image,0)==0);
    assert(n==16 && memcmp(r,"FTDR",4)==0 && calls==1 && c.called);
    for(offset=0;offset<1080;offset+=256) {
        unsigned count=1080-offset<256?1080-offset:256;
        request(q,2,++seq,offset,count);
        assert(diagnostic_dispatch(&c,q,16,r,sizeof(r),&n,call,read_image,0)==0);
        assert(n==16+count && memcmp(r+16,image+offset,count)==0);
    }
    assert(diagnostic_dispatch(&c,q,16,r,sizeof(r),&n,call,read_image,0)==-1 && n==0 && c.failed);
    memset(&c,0,sizeof(c));request(q,2,1,0,1);
    assert(diagnostic_dispatch(&c,q,16,r,sizeof(r),&n,call,read_image,0)==-1 && calls==1);
    memset(&c,0,sizeof(c));request(q,1,1,0,0);
    assert(diagnostic_dispatch(&c,q,16,r,15,&n,call,read_image,0)==-1 && calls==1);
    memset(&c,0,sizeof(c));request(q,1,1,0,0);
    assert(diagnostic_dispatch(&c,q,16,r,sizeof(r),&n,call,read_image,0)==0);
    request(q,2,2,0,4);
    assert(diagnostic_dispatch(&c,q,16,r,sizeof(r),&n,call,short_read,0)==-1 && n==0);
    memset(&c,0,sizeof(c));c.sequence=16;c.called=1;request(q,2,17,0,1);
    assert(diagnostic_dispatch(&c,q,16,r,sizeof(r),&n,call,read_image,0)==-1);
    return 0;
}
