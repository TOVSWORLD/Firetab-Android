/* Owned callable Thumb entry; injected ABI pointer remains in r0. Compile only. */
.syntax unified
.thumb
.section .text.agent_entry,"ax",%progbits
.global diagnostic_agent_entry
.type diagnostic_agent_entry,%function
.thumb_func
diagnostic_agent_entry:
.Lbase:
    mov r3, sp
    adr r1, .Lbase
    ldr r2, .Lstack_offset
    add r1, r1, r2
    mov sp, r1
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
.size diagnostic_agent_entry, . - diagnostic_agent_entry
.section .agent_stack,"aw",%progbits
.balign 8
.global diagnostic_agent_stack_bottom
diagnostic_agent_stack_bottom:
    .space 2048
.global diagnostic_agent_stack_top
diagnostic_agent_stack_top:
