#!/usr/bin/env python3
"""Static source/DT CPU contract comparison; never performs an SMC or device IO."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def audit(root=ROOT):
    index = json.loads((root/'evidence/cpu-startup-contract/sources.json').read_text())
    sources = {}
    for record in index['records']:
        raw = (root/record['path']).read_bytes()
        if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Source hash/size mismatch: '+record['name'])
        sources[record['name']] = raw.decode()
    refs = []
    def require(name, needle):
        text = sources[name]
        if text.count(needle) != 1:
            raise ValueError('Expected unique source anchor: '+name+' '+needle)
        refs.append({'source': name, 'line': text[:text.index(needle)].count('\n')+1, 'anchor': needle})
    for name, needle in [('legacy_mt_boot', '.name = "mt-boot"'),
                         ('legacy_mt_boot', 'return spm_mtcmos_ctrl_cpu(cpu, STA_POWER_ON, 1);'),
                         ('legacy_mt_boot', 'spm_mtcmos_cpu_init();'),
                         ('legacy_mt_boot', 'return !spm_mtcmos_ctrl_cpu(cpu, STA_POWER_DOWN, 1);'),
                         ('ack_ops', 'dt_supported_cpu_ops[]'),
                         ('ack_psci', 'Using PSCI v0.1 Function IDs from DT'),
                         ('ack_psci', 'return __psci_cpu_on(psci_0_1_function_ids.cpu_on, cpuid, entry_point);'),
                         ('ack_psci', 'return __psci_cpu_on(PSCI_FN_NATIVE(0_2, CPU_ON), cpuid, entry_point);'),
                         ('ack_cpu_psci', 'psci_ops.cpu_on(cpu_logical_map(cpu), pa_secondary_entry)'),
                         ('legacy_power', 'return (*spm_cpu_mtcmos_ctrl_funcs[cpu]) (state, chkWfiBeforePdn);')]:
        require(name, needle)
    boot = sources['legacy_mt_boot'].split('static int mt_psci_cpu_boot', 1)[1].split('#ifdef', 1)[0]
    if not boot.index('cpu_psci_ops.cpu_boot(cpu)') < boot.index('if (ret < 0)') < boot.index('spm_mtcmos_ctrl_cpu(cpu, STA_POWER_ON, 1)'):
        raise ValueError('Legacy secondary boot/power sequencing differs')
    table = sources['ack_ops'].split('dt_supported_cpu_ops[]', 1)[1].split('};', 1)[0]
    if 'mt-boot' in sources['ack_ops'] or 'mt_cpu_psci_ops' in table:
        raise ValueError('ACK method coverage differs')
    header = sources['ack_header']
    base = int(re.search(r'#define PSCI_0_2_FN_BASE\s+(0x[0-9a-fA-F]+)', header)[1], 16)
    wide = int(re.search(r'#define PSCI_0_2_64BIT\s+(0x[0-9a-fA-F]+)', header)[1], 16)
    stock = json.loads((root/'evidence/stock-dtb/candidate-report.json').read_text())
    methods = []
    for dt in stock['dtbs']:
        f = dt['facts']
        if f['psci']['compatible']['value'] != 'arm,psci' or f['cpu0_enable_method']['value'] != 'mt-boot':
            raise ValueError('Stock DT contract differs')
        methods.append({'variant': f['version']['value'], 'cpu_method': 'mt-boot',
                        'psci_compatible': 'arm,psci', 'cpu_on_id': '0x'+f['psci']['cpu_on']['value']})
    return {'scope': 'Static reference-source comparison; no firmware/device execution', 'source_anchors': refs,
            'stock_dt_contracts': methods, 'ack_supports_mt_boot_method': False,
            'legacy_secondary_sequence': ['generic PSCI cpu_boot', 'return on error', 'host-side SPM MTCMOS power-on'],
            'ack_generic_secondary_sequence': ['PSCI CPU_ON with secondary_entry address'],
            'ack_legacy_psci_ids_supported': True, 'ack_arm64_psci_v02_cpu_on_id': hex(base+wide+3),
            'stock_explicit_cpu_on_id': '0x84000003',
            'lk_primary_transition_smc_id': '0x82000200',
            'installed_monitor_supports_donor_v02_and_64bit_call': None,
            'legacy_reference_matches_installed_kernel_binary': False,
            'conservative_future_diagnostic_scope': 'primary CPU only; maxcpus=1, no CPU hotplug/suspend/off; not an assembled/tested configuration',
            'primary_entry_verified': False, 'secondary_cpu_boot_verified': False,
            'suspend_off_verified': False, 'physical_boot_verified': False}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
