/* Owned bounded polling core for source-reviewed 8250-style regshift-2 layout. */
#include "uart.h"
int diagnostic_uart_emit(volatile uint32_t *regs, const uint8_t *data,
                         size_t length, uint32_t budget) {
    size_t sent=0;
    if (!length) return 0;
    if (!regs || !data || length>64 || !budget || budget>4096) return -1;
    while(sent<length && budget) {
        /* DLAB would alias register zero to divisor latch, not transmit data. */
        if (regs[3] & 0x80u) return sent?(int)sent:-1;
        budget--;
        if (regs[5] & 0x20u) {
            regs[0]=data[sent];
            sent++;
        }
    }
    return (int)sent;
}
