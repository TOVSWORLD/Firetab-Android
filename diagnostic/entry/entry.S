/* Owned ARMv7 compile-only experiment. No peripheral or external calls. */
.syntax unified
.arm
.section .diag_entry,"awx",%progbits
.global diagnostic_entry
.type diagnostic_entry,%function
diagnostic_entry:
    adr r0, diagnostic_entry
    ldr r1, .Lstack_offset
    add sp, r0, r1
    adr r1, diagnostic_marker
    movw r2, #0x4b31
    movt r2, #0x4654
    str r2, [r1]
.Lstop:
    b .Lstop
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
