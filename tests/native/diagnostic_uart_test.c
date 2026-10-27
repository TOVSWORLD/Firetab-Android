/* Native synthetic register arrays only; no physical MMIO. */
#include <assert.h>
#include "uart.h"
#include "marker.h"
#include <string.h>
int main(void) {
    volatile uint32_t regs[6]={0};const uint8_t data[]={0x46,0x54,0x0a};
    regs[5]=0x20;
    assert(diagnostic_uart_emit(regs,data,3,3)==3 && regs[0]==0x0a);
    assert(diagnostic_uart_emit(regs,data,3,1)==1 && regs[0]==0x46);
    regs[5]=0;regs[0]=0x99;
    assert(diagnostic_uart_emit(regs,data,3,4096)==0 && regs[0]==0x99);
    regs[3]=0x80;regs[5]=0x20;
    assert(diagnostic_uart_emit(regs,data,3,3)==-1 && regs[0]==0x99);
    regs[3]=0;
    assert(diagnostic_uart_emit(regs,data,65,3)==-1);
    assert(diagnostic_uart_emit(regs,data,3,0)==-1);
    assert(diagnostic_uart_emit(regs,data,3,4097)==-1);
    assert(diagnostic_uart_emit(0,data,3,3)==-1);
    assert(diagnostic_uart_emit(0,0,0,0)==0);
    size_t length=99;const uint8_t *text=diagnostic_marker_text(DIAG_ENTRY,&length);
    assert(length==11 && memcmp(text,"FTD1 ENTRY\n",length)==0);
    text=diagnostic_marker_text(DIAG_RETURN,&length);
    assert(length==12 && memcmp(text,"FTD1 RETURN\n",length)==0);
    text=diagnostic_marker_text(DIAG_ERROR,&length);
    assert(length==11 && memcmp(text,"FTD1 ERROR\n",length)==0);
    assert(diagnostic_marker_text((enum diagnostic_log_marker)99,&length)==0 && length==0);
    assert(diagnostic_uart_marker(regs,(enum diagnostic_log_marker)99,4096)==-1);
    regs[5]=0x20;
    assert(diagnostic_uart_marker(regs,DIAG_ENTRY,11)==11 && regs[0]==10);
    assert(diagnostic_uart_marker(regs,DIAG_RETURN,1)==1 && regs[0]=='F');
    return 0;
}
