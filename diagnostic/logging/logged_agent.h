#ifndef DIAGNOSTIC_LOGGED_AGENT_H
#define DIAGNOSTIC_LOGGED_AGENT_H
#include "../protocol/agent.h"
struct diagnostic_log_result {
    int agent_invoked, agent_result, entry_queued, exit_queued, logging_complete;
};
/* Explicit opt-in only; requires exclusive qualified UART mapping and caller ABI.
 * Failure may follow agent invocation: inspect result, never retry automatically.
 */
int diagnostic_logged_run(const struct diagnostic_agent_io *io, volatile uint32_t *registers,
                          uint32_t total_poll_budget, struct diagnostic_log_result *result);
#endif
