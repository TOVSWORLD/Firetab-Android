/* Owned bounded protocol core. No USB, MMIO, global memory map or firmware entry. */
#include "dispatcher.h"
static uint16_t le16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}
static uint32_t le32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
int diagnostic_dispatch(struct diagnostic_context *c,
    const uint8_t *q, size_t n, uint8_t *r, size_t capacity, size_t *written,
    diagnostic_call call, diagnostic_read read, void *opaque) {
    uint16_t offset, length;
    uint32_t sequence;
    uint8_t operation;
    size_t i;
    if (written) *written = 0;
    if (!c) return -1;
    if (!q || !r || !written || c->failed || c->busy || n != 16) goto fail;
    if (q[0]!='F' || q[1]!='T' || q[2]!='D' || q[3]!='Q' ||
        q[4]!=1 || le16(q+6)!=0) goto fail;
    operation=q[5]; sequence=le32(q+8); offset=le16(q+12); length=le16(q+14);
    if (c->sequence>=16 || sequence!=c->sequence+1 || sequence>16) goto fail;
    if (operation==1) {
        if (c->called || offset || length || !call) goto fail;
    } else if (operation==2) {
        if (!c->called || !length || length>256 || offset>1080-length || !read) goto fail;
    } else goto fail;
    if (capacity < (size_t)16+length) goto fail;
    c->busy=1;
    if (operation==1) {
        if (call(opaque)!=0 || c->failed) goto fail;
        c->called=1;
    } else {
        /* Read callback must fill exactly length bytes and return that count. */
        if (read(opaque,offset,length,r+16)!=(int)length || c->failed) goto fail;
    }
    for (i=0;i<16;i++) r[i]=q[i];
    r[3]='R';
    c->sequence=sequence; c->busy=0;
    *written=(size_t)16+length;
    return 0;
fail:
    c->failed=1; c->busy=0;
    return -1;
}
