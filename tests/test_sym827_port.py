import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PORT = ROOT / 'projects/firetabs-android/kernel/regulator-port'
SPEC = importlib.util.spec_from_file_location('sym_apply', ROOT / 'scripts/apply_sym827_port.py')
APPLY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APPLY)


def function(source, name):
    start = source.index('static int ' + name + '(')
    brace = source.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]


class Sym827Port(unittest.TestCase):
    def fixture(self, tmp):
        lock = json.loads((PORT / 'inputs.json').read_text())
        target = Path(tmp) / lock['target']
        target.parent.mkdir(parents=True)
        target.write_bytes((ROOT / 'evidence/sym827-port/fan53555.c').read_bytes())
        return lock, target

    def test_preflight_and_reapply_no_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock, target = self.fixture(tmp)
            original = target.read_bytes()
            with self.assertRaises(ValueError): APPLY.apply(Path(tmp), 'wrong')
            self.assertEqual(target.read_bytes(), original)
            APPLY.apply(Path(tmp), lock['ack_commit'])
            output = target.read_bytes()
            self.assertEqual(hashlib.sha256(output).hexdigest(), lock['patched_sha256'])
            with self.assertRaises(ValueError): APPLY.apply(Path(tmp), lock['ack_commit'])
            self.assertEqual(target.read_bytes(), output)

    def test_bad_source_and_expected_output_leave_target_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock, target = self.fixture(tmp)
            original = target.read_bytes()
            bad = dict(lock, patched_sha256='0' * 64)
            real_loads = json.loads
            with patch.object(APPLY.json, 'loads', side_effect=lambda s: bad if s == (PORT / 'inputs.json').read_text() else real_loads(s)):
                with self.assertRaises(ValueError): APPLY.apply(Path(tmp), lock['ack_commit'])
            self.assertEqual(target.read_bytes(), original)
            target.write_bytes(original + b'\n')
            with self.assertRaises(ValueError): APPLY.apply(Path(tmp), lock['ack_commit'])
            self.assertEqual(target.read_bytes(), original + b'\n')

    def test_actual_c_identity_range_banks_and_existing_vendor_preservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock, target = self.fixture(tmp)
            original = target.read_text()
            APPLY.apply(Path(tmp), lock['ack_commit'])
            source = target.read_text()
            # Every pre-existing C function except setup/probe is exactly retained.
            import re
            for name in re.findall(r'static int (\w+)\(', original):
                if name not in {'fan53555_device_setup', 'fan53555_regulator_probe'}:
                    self.assertEqual(function(original, name), function(source, name))
            self.assertNotIn('silergy,sym827-regulator', source)
            probe = function(source, 'fan53555_regulator_probe')
            self.assertLess(probe.index('fan53555_sym827_validate'), probe.index('fan53555_device_setup'))
            self.assertLess(probe.index('Failed to get chip Rev'), probe.index('fan53555_sym827_validate'))
            # Compile actual selected source functions, declarations and tables.
            prefix = source[source.index('/* Voltage setting */'):source.index('static int fan53555_set_suspend_voltage')]
            prefix = prefix.replace('struct regulator_desc desc;', 'int desc;')
            tables = source[source.index('static const unsigned int slew_rates'):source.index('static const struct regulator_ops')]
            names = ['fan53526_voltages_setup_fairchild', 'fan53555_voltages_setup_fairchild', 'fan53555_voltages_setup_rockchip', 'rk8602_voltages_setup_rockchip', 'fan53555_sym827_validate', 'fan53555_voltages_setup_sym827', 'fan53555_voltages_setup_silergy', 'fan53526_voltages_setup_tcs', 'fan53555_device_setup']
            harness = r'''
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <errno.h>
#define BIT(n) (1U << (n))
#define GENMASK(h,l) ((~0U >> (31-(h))) & (~0U << (l)))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define dev_err(...) ((void)0)
#define FAN53555_VSEL_ID_0 0
#define FAN53555_VSEL_ID_1 1
typedef uint32_t u32;
struct device_node { int count, error, gpio; u32 selector; };
struct fan53555_platform_data { unsigned int sleep_vsel_id; };
static int of_property_count_u32_elems(struct device_node *n, const char *p) { (void)p; return n->count; }
static int of_property_read_u32(struct device_node *n, const char *p, u32 *v) { (void)p; *v=n->selector; return n->error; }
static const void *of_find_property(struct device_node *n, const char *p, void *l) { (void)l; return n->gpio && ((!strcmp(p,"vsel-gpio") && n->gpio==1) || (!strcmp(p,"vsel-gpios") && n->gpio==2) || (!strcmp(p,"en-gpio") && n->gpio==3)) ? n : NULL; }
'''
            harness += prefix + tables + '\n'.join(function(source, n) for n in names)
            harness += function(original, 'fan53555_device_setup').replace('fan53555_device_setup(', 'old_device_setup(', 1)
            harness += r'''
int main(void) {
 for(int vendor=0;vendor<=FAN53526_VENDOR_TCS;vendor++) for(int id=0;id<16;id++) for(int rev=0;rev<16;rev++) for(unsigned bank=0;bank<4;bank++) {
  struct fan53555_device_info a={0}, b={0};struct fan53555_platform_data p={bank};
  a.vendor=vendor;a.chip_id=id;a.chip_rev=rev;b=a;
  assert(fan53555_device_setup(&a,&p)==old_device_setup(&b,&p));
  assert(!memcmp(&a,&b,sizeof(a)));
 }
 struct device_node n={1,0,0,1};
 for (unsigned id=0; id<256; id++) for(unsigned rev=0; rev<256; rev++) {
  int expected=((id&0xe0)==0x80 && (id&15)==1 && (rev&15)==12);
  assert((fan53555_sym827_validate(&n,id,rev,1)==0)==expected);
 }
 assert(fan53555_sym827_validate(NULL,0x81,12,1)==-EINVAL);
 for(int count=-2; count<4; count++) { n.count=count; assert((fan53555_sym827_validate(&n,0x81,12,1)==0)==(count==1)); }
 n.count=1;
 for(unsigned selector=0; selector<4; selector++) for(unsigned pdata=0;pdata<4;pdata++) { n.selector=selector; assert((fan53555_sym827_validate(&n,0x81,12,pdata)==0)==(selector<2 && selector==pdata)); }
 n.selector=1;n.error=-EIO;assert(fan53555_sym827_validate(&n,0x81,12,1)==-EINVAL);n.error=0;
 for(int gpio=1;gpio<4;gpio++){n.gpio=gpio;assert(fan53555_sym827_validate(&n,0x81,12,1)==-EINVAL);}n.gpio=0;
 for(int id=0;id<16;id++) for(int rev=0;rev<16;rev++) {
  struct fan53555_device_info di={.vendor=FAN53555_VENDOR_SYM827,.chip_id=id,.chip_rev=rev};
  struct fan53555_platform_data p={.sleep_vsel_id=1};
  int ok=(id==1 && rev==12);
  assert((fan53555_device_setup(&di,&p)==0)==ok);
  if(ok){ assert(di.vsel_min==600000 && di.vsel_step==12500 && di.vsel_count==64);assert(di.vol_reg==0 && di.sleep_reg==1 && di.mode_mask==64 && di.enable_time==400); for(unsigned v=0;v<64;v++) assert(di.vsel_min+v*di.vsel_step<=1387500);assert(di.vsel_min+63*di.vsel_step==1387500); }
  struct fan53555_device_info old={.vendor=FAN53555_VENDOR_SILERGY,.chip_id=id,.chip_rev=rev};
  assert((fan53555_device_setup(&old,&p)==0)==(id==8 || id==9));
  if(id==8 || id==9) assert(old.vsel_min==712500 && old.vsel_step==12500);
 }
 for(unsigned bank=0;bank<4;bank++) {
  struct fan53555_device_info di={.vendor=FAN53555_VENDOR_SYM827,.chip_id=1,.chip_rev=12};struct fan53555_platform_data p={bank};
  assert((fan53555_device_setup(&di,&p)==0)==(bank<2));
  if(bank<2){ assert(di.vol_reg==1-bank && di.sleep_reg==bank && di.en_reg==di.vol_reg && di.mode_reg==di.vol_reg); }
 }
 return 0;
}
'''
            c = Path(tmp) / 'ram.c'; c.write_text(harness)
            compiler = shutil.which('cc')
            self.assertIsNotNone(compiler)
            subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined', str(c), '-o', str(Path(tmp)/'ram')], check=True, stdout=subprocess.PIPE, stderr=None)
            subprocess.run([str(Path(tmp)/'ram')], check=True)
