/* Owned explicit logging integration. No default address or boot-entry hook. */
#include "logged_agent.h"
#include "marker.h"
int diagnostic_logged_run(const struct diagnostic_agent_io *io,volatile uint32_t *regs,
                          uint32_t budget,struct diagnostic_log_result *r) {
    uint32_t first;
    if(!r)return -1;
    r->agent_invoked=0;r->agent_result=-1;r->entry_queued=0;r->exit_queued=0;r->logging_complete=0;
    if(!io || !regs || budget<2 || budget>4096)return -1;
    first=budget/2;
    r->entry_queued=diagnostic_uart_marker(regs,DIAG_ENTRY,first);
    if(r->entry_queued!=11)return -1;
    r->agent_invoked=1;
    r->agent_result=diagnostic_agent_run(io);
    r->exit_queued=diagnostic_uart_marker(regs,r->agent_result==0?DIAG_RETURN:DIAG_ERROR,budget-first);
    if(r->exit_queued!=(r->agent_result==0?12:11))return -1;
    r->logging_complete=1;
    return 0;
}
