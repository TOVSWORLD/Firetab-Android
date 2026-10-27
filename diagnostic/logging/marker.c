/* Owned fixed diagnostic markers; offset-indexed storage avoids absolute pointer tables. */
#include "marker.h"
static const uint8_t texts[3][13]={"FTD1 ENTRY\n","FTD1 RETURN\n","FTD1 ERROR\n"};
static const uint8_t lengths[3]={11,12,11};
const uint8_t *diagnostic_marker_text(enum diagnostic_log_marker marker,size_t *length) {
    unsigned index=(unsigned)marker-1;
    if(!length)return 0;
    *length=0;
    if(index>=3)return 0;
    *length=lengths[index];
    return texts[index];
}
int diagnostic_uart_marker(volatile uint32_t *regs,enum diagnostic_log_marker marker,uint32_t budget) {
    size_t length;const uint8_t *text=diagnostic_marker_text(marker,&length);
    if(!text)return -1;
    return diagnostic_uart_emit(regs,text,length,budget);
}
