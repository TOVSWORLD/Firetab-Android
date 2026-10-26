/* Native host vector runner; synthetic memory only. Not firmware or transport. */
#include <stdio.h>
#include <string.h>
#include "dispatcher.h"
static uint8_t image[1080];
static int call(void *unused) { (void)unused; image[48]=0x31;return 0; }
static int read_image(void *unused,uint16_t o,uint16_t n,uint8_t *p) {
    (void)unused;memcpy(p,image+o,n);return n;
}
int main(void) {
    struct diagnostic_context c={0};uint8_t q[32],r[272],header[2];size_t written;unsigned n;
    while(fread(header,1,2,stdin)==2) {
        n=(unsigned)header[0]|((unsigned)header[1]<<8);
        if(n>sizeof(q) || fread(q,1,n,stdin)!=n)return 2;
        int result=diagnostic_dispatch(&c,q,n,r,sizeof(r),&written,call,read_image,0);
        if(fputc(result==0?0:1,stdout)==EOF)return 3;
        if(fputc((int)(written&255),stdout)==EOF || fputc((int)(written>>8),stdout)==EOF)return 3;
        if(fwrite(r,1,written,stdout)!=written)return 3;
    }
    return ferror(stdin)?2:0;
}
