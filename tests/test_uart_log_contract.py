from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_uart_log_contract import assess, REQUIRED, pinmux


def encode(value):return ' '.join(format(x,'x') for x in value.encode()+b'\0')


class UartLogContractTests(unittest.TestCase):
    def test_builtin_driver_and_alias_do_not_prove_a_physical_console(self):
        nodes={'/chosen':{'stdout-path':encode('serial0:921600n8'),'bootargs':encode('nr_cpus=1 maxcpus=0')},
               '/aliases':{'serial0':encode('/soc/serial')},
               '/soc/serial':{'compatible':encode('mediatek,mt8163-uart\0mediatek,mt6577-uart')}}
        config='\n'.join('CONFIG_'+x+'=y' for x in REQUIRED)
        result=assess(nodes,config)
        self.assertTrue(result['all_required_driver_symbols_builtin'])
        self.assertTrue(result['mt6577_driver_fallback_present'])
        self.assertFalse(result['explicit_earlycon_request_in_dt'])
        self.assertFalse(result['usable_log_path_qualified'])
        self.assertFalse(assess(nodes,config.replace('MT6577=y','MT6577=m'))['all_required_driver_symbols_builtin'])

    def test_unresolved_stdout_fails_and_arguments_are_only_scoped_to_dt(self):
        with self.assertRaises(ValueError):assess({'/chosen':{}},'')
        nodes={'/chosen':{'stdout-path':encode('/uart'),'bootargs':encode('earlycon console=ttyS0')},
               '/uart':{'status':encode('disabled')}}
        result=assess(nodes,'')
        self.assertTrue(result['explicit_earlycon_request_in_dt'])
        self.assertEqual(result['uart_status'],'disabled')
        self.assertFalse(result['loader_preserves_dt_or_args_verified'])

    def test_pinmux_resolves_phandles_and_rejects_ambiguous_identity(self):
        nodes={'/pins':{'phandle':'0 0 0 18'},
               '/pins/group':{'pinmux':'0 0 4f 1 0 0 50 1'}}
        self.assertEqual(pinmux(nodes,{'pinctrl-0':'0 0 0 18'}),[
            {'soc_gpio_index':79,'mux_function':1},{'soc_gpio_index':80,'mux_function':1}])
        nodes['/alias']={'phandle':'0 0 0 18'}
        with self.assertRaises(ValueError):pinmux(nodes,{'pinctrl-0':'0 0 0 18'})
