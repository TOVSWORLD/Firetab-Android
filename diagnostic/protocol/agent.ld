OUTPUT_FORMAT("elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(diagnostic_agent_entry)
SECTIONS
{
  DIAGNOSTIC_BASE = DEFINED(DIAGNOSTIC_LINK_BASE) ? DIAGNOSTIC_LINK_BASE : 0;
  . = DIAGNOSTIC_BASE;
  .text : { *(.text.agent_entry) *(.text .text.*) }
  .rodata : { *(.rodata .rodata.*) }
  .agent_context : { *(.agent_context) }
  .data : { *(.data .data.*) }
  .bss : { *(.bss .bss.*) *(COMMON) }
  .agent_stack ALIGN(8) : { *(.agent_stack) }
  /DISCARD/ : { *(.comment) *(.ARM.attributes) *(.ARM.exidx*) }
}
ASSERT((diagnostic_agent_entry & ~1) == DIAGNOSTIC_BASE, "Thumb entry must be image offset zero")
ASSERT((diagnostic_agent_stack_top % 8) == 0, "Stack alignment")
ASSERT(diagnostic_agent_stack_top - diagnostic_agent_stack_bottom == 2048, "Stack size")
ASSERT(diagnostic_agent_stack_top - DIAGNOSTIC_BASE <= 65536, "Bounded image")
