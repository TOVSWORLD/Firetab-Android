#!/usr/bin/env python3
"""Read-only host checks for a full Android build. Does not install anything."""
import json
import os
from pathlib import Path
import platform
import shutil
import tempfile

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(dir=root) as tmp:
    p = Path(tmp)
    (p / 'CaseCheck').write_text('a')
    case_sensitive = not (p / 'casecheck').exists()
try:
    ram = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 2**30
except (ValueError, OSError):
    ram = None
free = shutil.disk_usage(root).free / 2**30
checks = {
    'linux_x86_64': platform.system() == 'Linux' and platform.machine() == 'x86_64',
    'case_sensitive_filesystem': case_sensitive,
    'free_disk_at_least_400_GiB': free >= 400,
    'RAM_at_least_32_GiB': ram is not None and ram >= 32,
}
print(json.dumps(dict(system=platform.system(), machine=platform.machine(),
                     free_GiB=round(free, 1), RAM_GiB=ram, checks=checks), indent=2))
raise SystemExit(0 if all(checks.values()) else 2)
