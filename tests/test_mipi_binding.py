import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_douglas_bindings import apply_locked_proposal
import validate_mipi_dependencies as guard
E=ROOT/'evidence/mipi-binding'


class MipiBinding(unittest.TestCase):
    def test_locked_patch_and_accepted_source_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'phy/mediatek,dsi-phy.yaml';p.parent.mkdir();p.write_bytes((E/'dsi-original.yaml').read_bytes());before=p.read_bytes()
            with self.assertRaises(ValueError):apply_locked_proposal(Path(tmp),'wrong','mt8163-mipi-tx.json')
            self.assertEqual(p.read_bytes(),before);apply_locked_proposal(Path(tmp),'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-mipi-tx.json');self.assertEqual(p.read_bytes(),(E/'dsi-proposed.yaml').read_bytes())
            with self.assertRaises(ValueError):apply_locked_proposal(Path(tmp),'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-mipi-tx.json')
        build=json.loads((ROOT/'evidence/mipi-kernel-integration/build-result.json').read_text());lock=json.loads((ROOT/'projects/firetabs-android/kernel/mipi-port/inputs.json').read_text());self.assertTrue(build['passed']);self.assertEqual(build['repository_head'],'b5e12688ced84a917657d928365dec969eb66a1c')
        for row in lock['files']:self.assertEqual(build['final_hashes']['source/'+row['target']],row['patched_sha256'])
        for symbol in ['PHY_MTK_MIPI_DSI','RESET_CONTROLLER','GENERIC_PHY']:self.assertEqual(build['resolved_symbols'][symbol],'y')

    def test_actual_source_graph_and_negative_mutations(self):
        graph=json.loads((E/'captured-graph.json').read_text());r=guard.validate(graph);self.assertFalse(r['runtime_qualified']);self.assertTrue(r['phy_and_dsi_remain_disabled'])
        for key,val in [('compatible',['mediatek,mt8173-mipi-tx']),('reg',[0,0x10215000,0,0x68]),('reg',[0,0x10215004,0,0x1000]),('#clock-cells',[1]),('#phy-cells',[1]),('status',['okay']),('clocks',[22,14]),('resets',[2,11]),('resets',[2]),('phandle',[]),('nvmem-cells',[1]),('drive-strength-microamp',[4600]),('assigned-clock-rates',[26000000])]:
            n=copy.deepcopy(graph);n['nodes'][guard.PHY][key]=val
            with self.assertRaises(ValueError,msg=key):guard.validate(n)
        for path,key,val in [('/soc/clock-controller@1000c000','status',['disabled']),('/soc/clock-controller@1000c000','#clock-cells',[0]),('/soc/clock-controller@10001000','#reset-cells',[0]),('/clocks/oscillator-26m','clock-frequency',[25000000]),(guard.DSI,'phys',[1]),(guard.DSI,'status',['okay']),(guard.DSI,'clocks',[1]),(guard.DSI,'clock-names',['engine','digital','wrong'])]:
            n=copy.deepcopy(graph);n['nodes'][path][key]=val
            with self.assertRaises(ValueError,msg=path+key):guard.validate(n)

    def test_frozen_type_pipeline_and_exact_failed_full_deltas(self):
        controls=json.loads((E/'controls.json').read_text());self.assertEqual(controls['count'],35);self.assertTrue(controls['type_policy_pipeline_retained']);self.assertTrue(controls['old_soc_policy_structurally_preserved'])
        for kind,before,after in [('canonical',32,31),('isolated',26,25)]:
            d=json.loads((E/(kind+'-delta.json')).read_text());r=json.loads((E/(kind+'-report.json')).read_text());self.assertEqual((d['before'],d['after']),(before,after));self.assertEqual(len(d['removed']),1);self.assertEqual(d['removed'][0]['node'],guard.PHY);self.assertFalse(d['added']);self.assertFalse(r['passed']);self.assertEqual(r['wrapper_exit'],1)
            ds=json.loads((E/(kind+'-diagnostics.json')).read_text());self.assertEqual(len(ds),after);self.assertTrue(any(x['node']=='/soc/clock-controller@11220000/audio-controller' and x['type']=='unmatched' for x in ds))
        for path,sha in json.loads((E/'source-contract.json').read_text())['sha256'].items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),sha)
