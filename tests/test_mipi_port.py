import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from audit_mipi_source import function
spec=importlib.util.spec_from_file_location('mipi_apply',ROOT/'scripts/apply_mipi_port.py');apply=importlib.util.module_from_spec(spec);spec.loader.exec_module(apply)
PORT=ROOT/'projects/firetabs-android/kernel/mipi-port';E=ROOT/'evidence/mipi-kernel-integration'


def fixture(root):
    lock=json.loads((PORT/'inputs.json').read_text())
    for row in lock['files']:
        dest=root/row['target'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/row['source']).read_bytes())
    for row in lock['build_inputs']:(root/row['target']).write_bytes((ROOT/row['source']).read_bytes())
    (root/'drivers/phy/mediatek/phy-mtk-io.h').write_bytes((ROOT/'evidence/mipi-source/phy-mtk-io.h').read_bytes())
    return lock


def compile_run(code):
    with tempfile.TemporaryDirectory() as tmp:
        c=Path(tmp)/'ram.c';binary=Path(tmp)/'ram';c.write_text(code)
        r=subprocess.run(['cc','-std=gnu11','-Wall','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
        if r.returncode:raise AssertionError(r.stderr)
        subprocess.run([str(binary)],check=True)


class MipiPort(unittest.TestCase):
    def patched(self,root):
        lock=fixture(root);apply.apply(root,lock['ack_commit']);return {Path(x['target']).name:(root/x['target']).read_text() for x in lock['files']}

    def test_all_target_preflight_source_helper_output_and_reapply_negatives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);lock=fixture(root);before={r['target']:(root/r['target']).read_bytes() for r in lock['files']}
            with self.assertRaises(ValueError):apply.apply(root,'wrong')
            second=root/lock['files'][1]['target'];second.write_bytes(before[lock['files'][1]['target']]+b'\n')
            with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
            for row in lock['files']:
                if row['target']!=lock['files'][1]['target']:self.assertEqual((root/row['target']).read_bytes(),before[row['target']])
            second.write_bytes(before[lock['files'][1]['target']]);header=root/lock['files'][2]['target'];header.write_bytes(header.read_bytes()+b'\n')
            with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
            header.write_bytes(before[lock['files'][2]['target']]);helper=root/'drivers/phy/mediatek/phy-mtk-io.h';helper.write_bytes(helper.read_bytes()+b'\n')
            with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
            helper.write_bytes((ROOT/'evidence/mipi-source/phy-mtk-io.h').read_bytes())
            bad=json.loads(json.dumps(lock));bad['files'][1]['patched_sha256']='0'*64
            real_loads=json.loads
            with patch.object(apply.json,'loads',side_effect=lambda x:bad if x==(PORT/'inputs.json').read_text() else real_loads(x)):
                with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
            for path,data in before.items():self.assertEqual((root/path).read_bytes(),data)
            apply.apply(root,lock['ack_commit']);after={path:(root/path).read_bytes() for path in before}
            with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
            for path,data in after.items():self.assertEqual((root/path).read_bytes(),data)

    def test_actual_patched_pll_rate_reference_cache_and_register_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            sources=self.patched(Path(tmp));soc=sources['phy-mtk-mipi-dsi-mt8173.c'];generic=sources['phy-mtk-mipi-dsi.c']
            constants=soc[soc.index('#define MIPITX_DSI_CON'):soc.index('static int mtk_mipi_tx_pll_prepare(')]
            io='\n'.join(x for x in (ROOT/'evidence/mipi-source/phy-mtk-io.h').read_text().splitlines() if not x.startswith('#include'))
            names=['mtk_mipi_tx_pll_prepare_mt8163','mtk_mipi_tx_pll_unprepare_mt8163','mtk_mipi_tx_pll_round_rate_mt8163','mtk_mipi_tx_pll_set_rate_mt8163']
            code=constants+'\n'+io+'\n'+'\n'.join(function(soc,n) for n in names)+'\n'+function(generic,'mtk_mipi_tx_pll_recalc_rate')
            code+='\n'+re.search(r'static const struct clk_ops mtk_mipi_tx_pll_ops_mt8163 = \{.*?\n};',soc,re.S).group()
            compile_run((E/'pll-ram.c.in').read_text().replace('/* ACTUAL_SOURCE */',code))

    def test_actual_probe_power_failure_order_and_original_soc_differential(self):
        with tempfile.TemporaryDirectory() as tmp:
            sources=self.patched(Path(tmp));source=sources['phy-mtk-mipi-dsi.c'];header=sources['phy-mtk-mipi-dsi.h']
            structs=header[header.index('struct mtk_mipitx_data {'):header.index('struct mtk_mipi_tx *mtk_mipi_tx_from_clk_hw')]
            code='\n'.join(function(source,n) for n in ['mtk_mipi_tx_power_on','mtk_mipi_tx_power_off'])+'\n'
            code+=re.search(r'static const struct phy_ops mtk_mipi_tx_ops = \{.*?\n};',source,re.S).group()+'\n'
            code+='\n'.join(function(source,n) for n in ['mtk_mipi_tx_get_calibration_datal','mtk_mipi_tx_mt8163_preflight','mtk_mipi_tx_probe'])
            original=(ROOT/'evidence/mipi-source/phy-mtk-mipi-dsi.c').read_text();code+='\n'+function(original,'mtk_mipi_tx_probe').replace('mtk_mipi_tx_probe(', 'old_probe(',1)
            compile_run((E/'probe-ram.c.in').read_text().replace('/* ACTUAL_STRUCTS */',structs).replace('/* ACTUAL_FUNCTIONS */',code))

    def test_prior_soc_functions_and_ops_remain_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            sources=self.patched(Path(tmp))
            for name,source in sources.items():
                if name.endswith('.h'):continue
                original=(ROOT/'evidence/mipi-source'/name).read_text()
                for fn in re.findall(r'^(?:static )?(?:int|long|unsigned long|void) (\w+)\(',original,re.M):
                    if fn!='mtk_mipi_tx_probe':self.assertEqual(function(original,fn),function(source,fn))
                for ops in re.findall(r'(?:static )?const struct (?:clk_ops|mtk_mipitx_data) \w+ = \{.*?\n};',original,re.S):self.assertIn(ops,source)
            self.assertIn('device_reset(dev)',sources['phy-mtk-mipi-dsi.c']);self.assertNotIn('device_reset_optional',sources['phy-mtk-mipi-dsi.c'])

    def test_definition_patch_and_build_inputs_drift_no_target_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'source';lock=fixture(root);before={r['target']:(root/r['target']).read_bytes() for r in lock['files']}
            port=Path(tmp)/'port';shutil.copytree(PORT,port)
            with patch.object(apply,'PORT',port):
                definition=port/'variant-definition.json';original=definition.read_bytes();definition.write_bytes(original+b'\n')
                with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
                definition.write_bytes(original);p=port/lock['patch'];p.write_bytes(p.read_bytes()+b'\n')
                with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
            build=root/lock['build_inputs'][0]['target'];build.write_bytes(build.read_bytes()+b'\n')
            with self.assertRaises(ValueError):apply.apply(root,lock['ack_commit'])
            for path,data in before.items():self.assertEqual((root/path).read_bytes(),data)
