#ifndef DIAGNOSTIC_MARKER_H
#define DIAGNOSTIC_MARKER_H
#include "uart.h"
enum diagnostic_log_marker { DIAG_ENTRY=1, DIAG_RETURN=2, DIAG_ERROR=3 };
/* Fixed literals only: no caller text, pointers, identifiers or memory dumps. */
const uint8_t *diagnostic_marker_text(enum diagnostic_log_marker marker, size_t *length);
int diagnostic_uart_marker(volatile uint32_t *registers,
                           enum diagnostic_log_marker marker, uint32_t poll_budget);
#endif
