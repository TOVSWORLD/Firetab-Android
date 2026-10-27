/* Owned compile-only bridge for an ARM-state caller passing no useful r0.
 * Embedded ABI is deliberately unbound: agent rejects null callbacks.
 */
.syntax unified
.arm
.section .text.agent_entry,"ax",%progbits
.global diagnostic_agent_entry
.type diagnostic_agent_entry,%function
diagnostic_agent_entry:
.Lbase:
    adr r1, .Lthumb + 1
    bx r1
.thumb
.Lthumb:
    mov r3, sp
    adr r1, .Lbase
    ldr r2, .Lstack_offset
    add r2, r1, r2
    mov sp, r2
    ldr r2, .Lcontext_offset
    add r0, r1, r2
    push {r4, r5, r6, lr}
    mov r4, r3
    bl diagnostic_agent_run
    mov r3, r4
    pop {r4, r5, r6, lr}
    mov sp, r3
    bx lr
.balign 4
.Lstack_offset:
    .word diagnostic_agent_stack_top - .Lbase
.Lcontext_offset:
    .word diagnostic_bridge_context - .Lbase
.size diagnostic_agent_entry, . - diagnostic_agent_entry
.section .agent_context,"aw",%progbits
.balign 4
.global diagnostic_bridge_context
diagnostic_bridge_context:
    .word 1, 6 /* ABI version and transaction count. */
    .word 0, 0, 0, 0, 0 /* receive/send/call/read/opaque: UNBOUND. */
.global diagnostic_bridge_context_end
diagnostic_bridge_context_end:
.section .agent_stack,"aw",%progbits
.balign 8
.global diagnostic_agent_stack_bottom
diagnostic_agent_stack_bottom:
    .space 2048
.global diagnostic_agent_stack_top
diagnostic_agent_stack_top:
