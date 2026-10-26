/* Owned compile-only AAPCS-style leaf experiment. No transport or hardware I/O. */
.syntax unified
.arm
.section .diag_entry,"awx",%progbits
.global diagnostic_entry
.type diagnostic_entry,%function
diagnostic_entry:
    mov r3, sp
    adr r0, diagnostic_entry
    ldr r1, .Lstack_offset
    add sp, r0, r1
    adr r1, diagnostic_marker
    movw r2, #0x4b31
    movt r2, #0x4654
    str r2, [r1]
    mov sp, r3
    mov r0, #0
    bx lr
.Lstack_offset:
    .word diagnostic_stack_top - diagnostic_entry
.global diagnostic_marker
diagnostic_marker:
    .word 0
.balign 8
.global diagnostic_stack_bottom
diagnostic_stack_bottom:
    .space 1024
.global diagnostic_stack_top
diagnostic_stack_top:
.size diagnostic_entry, . - diagnostic_entry
