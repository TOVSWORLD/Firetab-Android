/* Owned fixed diagnostic markers; no formatting or dynamic data. */
#include "marker.h"
const uint8_t *diagnostic_marker_text(enum diagnostic_log_marker marker,size_t *length) {
    const uint8_t *text;
    if (!length) return 0;
    *length=0;
    switch(marker) {
    case DIAG_ENTRY:text=(const uint8_t *)"FTD1 ENTRY\n";*length=sizeof("FTD1 ENTRY\n")-1;break;
    case DIAG_RETURN:text=(const uint8_t *)"FTD1 RETURN\n";*length=sizeof("FTD1 RETURN\n")-1;break;
    case DIAG_ERROR:text=(const uint8_t *)"FTD1 ERROR\n";*length=sizeof("FTD1 ERROR\n")-1;break;
    default:return 0;
    }
    return text;
}
int diagnostic_uart_marker(volatile uint32_t *regs,enum diagnostic_log_marker marker,uint32_t budget) {
    size_t length;const uint8_t *text=diagnostic_marker_text(marker,&length);
    if(!text)return -1;
    return diagnostic_uart_emit(regs,text,length,budget);
}
