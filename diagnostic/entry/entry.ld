OUTPUT_FORMAT("elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(diagnostic_entry)
SECTIONS
{
  . = 0;
  .diag_entry : { *(.diag_entry) }
  /DISCARD/ : { *(.comment) *(.ARM.attributes) }
}
ASSERT(diagnostic_entry == 0, "Entry must be zero based")
ASSERT((diagnostic_stack_top % 8) == 0, "Stack must be eight-byte aligned")
ASSERT(diagnostic_stack_top - diagnostic_stack_bottom == 1024, "Stack must be 1KiB")
ASSERT(diagnostic_marker < diagnostic_stack_bottom, "Marker must precede stack")
