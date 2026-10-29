import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_douglas_bindings import apply_locked_proposal
import validate_audsys_dependencies as guard
EVIDENCE=ROOT/'evidence/audsys-binding'


def extract(source,name):
    index=source.index(name+'(');start=source.rfind('\n',0,index)+1;brace=source.index('{',index);depth=1;end=brace+1
    while depth:
        if source[end]=='{':depth+=1
        elif source[end]=='}':depth-=1
        end+=1
    return source[start:end]


class Audsys(unittest.TestCase):
    def test_locked_binding_actual_patch_and_input_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);schema=root/'arm/mediatek/mediatek,audsys.yaml';schema.parent.mkdir(parents=True)
            schema.write_bytes((EVIDENCE/'audsys-original.yaml').read_bytes())
            before=schema.read_bytes()
            with self.assertRaises(ValueError):apply_locked_proposal(root,'wrong','mt8163-audsys.json')
            self.assertEqual(before,schema.read_bytes())
            apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-audsys.json')
            self.assertEqual(schema.read_bytes(),(EVIDENCE/'audsys-proposed.yaml').read_bytes())
            with self.assertRaises(ValueError):apply_locked_proposal(root,'d9318bdb4c34e8b2d997b4f67ced56b120b22b87','mt8163-audsys.json')

    def test_actual_probe_population_and_rollback_code_ram_only(self):
        source=(ROOT/'projects/firetabs-android/kernel/clock-port/overlay/drivers/clk/mediatek/clk-mt8163-audsys.c').read_text()
        code=(EVIDENCE/'probe-ram.c.in').read_text().replace('/* ACTUAL_WRAPPERS */',extract(source,'clk_mt8163_audio_probe')+'\n'+extract(source,'clk_mt8163_audio_remove'))
        with tempfile.TemporaryDirectory() as tmp:
            c=Path(tmp)/'probe.c';binary=Path(tmp)/'probe';c.write_text(code)
            r=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            r=subprocess.run([str(binary)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);self.assertIn('FIRETABS_AUDSYS_PARENT_RAM_PASS',r.stdout)

    def test_source_register_extent_and_consumer_graph(self):
        graph=json.loads((EVIDENCE/'captured-clock-graph.json').read_text());result=guard.validate(graph)
        self.assertEqual(result['source_layout']['required_extent_bytes'],0x5a8)
        self.assertEqual(len(result['audsys_clock_references']),15)
        self.assertTrue(result['child_remains_disabled']);self.assertFalse(result['child_binding_covered']);self.assertFalse(result['runtime_qualified'])
        parent=guard.PARENT;child=guard.CHILD
        for key,value in [('compatible',['mediatek,mt8173-audsys','syscon']),('reg',[0,0x11220000,0,0x400]),('reg',[0,0x11221000,0,0x1000]),('#clock-cells',[2]),('status',['disabled']),('phandle',[]),('reg-io-width',[1]),('big-endian',[]),('clocks',[16])]:
            changed=copy.deepcopy(graph);changed['nodes'][parent][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):guard.validate(changed)
        for key,value in [('status',['okay']),('compatible',['mediatek,mt2701-audio'])]:
            changed=copy.deepcopy(graph);changed['nodes'][child][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):guard.validate(changed)
        changed=copy.deepcopy(graph);changed['nodes'][child]['clocks']=[graph['nodes'][parent]['phandle'][0],19]
        with self.assertRaises(ValueError):guard.validate(changed)
        changed=copy.deepcopy(graph);changed['nodes'][child]['clocks']=[graph['nodes'][parent]['phandle'][0]]
        with self.assertRaises(ValueError):guard.validate(changed)
        changed=copy.deepcopy(graph);changed['nodes'][child]['assigned-clocks']=[graph['nodes'][parent]['phandle'][0],18]
        self.assertEqual(len(guard.validate(changed)['audsys_clock_references']),16)
        changed['nodes'][child]['assigned-clocks'][-1]=19
        with self.assertRaises(ValueError):guard.validate(changed)

    def test_exact_diagnostic_delta_and_child_not_hidden(self):
        for kind,before,after in [('canonical',34,33),('isolated',28,27)]:
            delta=json.loads((EVIDENCE/(kind+'-delta.json')).read_text());report=json.loads((EVIDENCE/(kind+'-report.json')).read_text())
            self.assertEqual((delta['before'],delta['after']),(before,after));self.assertEqual(delta['added'],[]);self.assertEqual(len(delta['removed']),1)
            self.assertTrue(delta['unmatched_disabled_afe_child_preserved']);self.assertFalse(report['passed'])
            self.assertEqual((EVIDENCE/(kind+'-mt8163-audsys-doc-validate.stderr')).read_bytes(),b'')

if __name__=='__main__':unittest.main()
