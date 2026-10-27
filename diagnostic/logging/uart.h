#ifndef DIAGNOSTIC_UART_H
#define DIAGNOSTIC_UART_H
#include <stdint.h>
#include <stddef.h>
/* Caller supplies qualified 32-bit register mapping; no physical address is selected.
 * Returns bytes queued, possibly partial. Never retry a partial message blindly.
 * Poll-count bound is not a time/MMIO-fault bound or transmit-drain guarantee.
 */
int diagnostic_uart_emit(volatile uint32_t *registers, const uint8_t *data,
                         size_t length, uint32_t poll_budget);
#endif
