#!/usr/bin/env python3
"""Audit public diagnostic DT/config, without device access or DT mutations."""
import hashlib
import json
from pathlib import Path
import re
from compare_pmic_dtb import snapshot

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=('SERIAL_EARLYCON','SERIAL_8250','SERIAL_8250_CONSOLE','SERIAL_8250_MT6577')


def string(raw):
    return bytes(int(x,16) for x in raw.split()).rstrip(b'\0').decode('ascii')



def cells(raw):
    data=bytes(int(x,16) for x in raw.split())
    if len(data)%4:
        raise ValueError('Malformed DT cells')
    return [int.from_bytes(data[i:i+4],'big') for i in range(0,len(data),4)]


def pinmux(nodes, uart):
    result=[]
    for ref in cells(uart.get('pinctrl-0','')):
        matches=[path for path,props in nodes.items() if cells(props.get('phandle',''))==[ref]]
        if len(matches)!=1:
            raise ValueError('Pin-control phandle unresolved or ambiguous')
        group=matches[0]
        for path,props in nodes.items():
            if path==group or path.startswith(group+'/'):
                for value in cells(props.get('pinmux','')):
                    result.append({'soc_gpio_index':value>>8,'mux_function':value&255})
    return result


def assess(nodes, config):
    chosen=nodes.get('/chosen',{})
    stdout=string(chosen.get('stdout-path',''))
    name,_,options=stdout.partition(':')
    target=name if name.startswith('/') else string(nodes.get('/aliases',{}).get(name,''))
    if not target or target not in nodes:
        raise ValueError('stdout target is unresolved')
    uart=nodes[target]
    compatibles=string(uart.get('compatible','')).split('\0')
    status=string(uart.get('status','')) or 'okay'
    resolved=dict(re.findall(r'^CONFIG_([A-Z0-9_]+)=(.*)$',config,re.M))
    args=string(chosen.get('bootargs','')).split()
    return {'stdout_target':target,'stdout_options':options,'uart_status':status,
        'mt6577_driver_fallback_present':'mediatek,mt6577-uart' in compatibles,
        'driver_config':{key:resolved.get(key,'n') for key in REQUIRED},
        'all_required_driver_symbols_builtin':all(resolved.get(key)=='y' for key in REQUIRED),
        'explicit_earlycon_request_in_dt':any(x=='earlycon' or x.startswith('earlycon=') for x in args),
        'explicit_console_request_in_dt':any(x.startswith('console=') for x in args),
        'clock_names':string(uart.get('clock-names','')).split('\0'),
        'resolved_default_soc_pinmux':pinmux(nodes,uart),
        'soc_pin_indices_are_pcb_pad_numbers':False,
        'dma_property_present':'dmas' in uart,'pin_control_property_present':'pinctrl-0' in uart,
        'loader_preserves_dt_or_args_verified':False,'firmware_uart_initialized_verified':False,
        'physical_pad_voltage_routing_verified':False,'usable_log_path_qualified':False}


def main():
    dtb=ROOT/'out/primary-only-dtb-reviewed/primary-only.dtb'
    lock=json.loads((ROOT/'evidence/primary-only/report.json').read_text())
    raw=dtb.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=lock['artifact']['sha256']:
        raise ValueError('Reviewed DTB identity mismatch')
    config=ROOT/'evidence/diagnostic-kernel/diagnostic.config'
    driver=ROOT/'evidence/console-storage/ack/drivers/tty/serial/8250/8250_mtk.c'
    records=json.loads((ROOT/'evidence/console-storage/sources.json').read_text())
    expected=next(x for x in records if x['path'].endswith('/8250_mtk.c'))
    if hashlib.sha256(driver.read_bytes()).hexdigest()!=expected['sha256']:
        raise ValueError('Pinned driver identity mismatch')
    report={'scope':'Reviewed public DT and source/config contract only',
        'dtb_sha256':lock['artifact']['sha256'],
        'config_sha256':hashlib.sha256(config.read_bytes()).hexdigest(),
        'driver_source':expected,
        'facts':assess(snapshot(ROOT/'work/dtb-tool/build/fdtget',dtb),config.read_text()),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
