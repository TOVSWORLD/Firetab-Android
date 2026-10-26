"""Generated host-only GPT fixture; contains no real device or firmware data."""
import struct
import zlib


def image(sector=512, total=128, mutate=None):
    data = bytearray(sector * total)
    table = bytearray(128 * 128)
    table[:16] = b'T' * 16
    table[16:32] = b'U' * 16
    struct.pack_into('<QQ', table, 32, 40, 50)
    table_sectors = (len(table) + sector - 1) // sector
    secondary_table = total - 1 - table_sectors
    for lba, alternate, table_lba in [(1, total-1, 2), (total-1, 1, secondary_table)]:
        block = bytearray(sector)
        block[:8] = b'EFI PART'
        struct.pack_into('<IIIIQQQQ', block, 8, 0x10000, 92, 0, 0,
                         lba, alternate, 2 + table_sectors, secondary_table - 1)
        block[56:72] = b'G' * 16
        struct.pack_into('<QIII', block, 72, table_lba, 128, 128, zlib.crc32(table))
        if mutate:
            mutate(lba, block, table)
        struct.pack_into('<I', block, 16, zlib.crc32(block[:92]))
        data[lba*sector:(lba+1)*sector] = block
        data[table_lba*sector:table_lba*sector+len(table)] = table
    return data

