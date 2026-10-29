import gzip
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from audit_usb_gadget_prerequisites import archive_inventory, audit, config_states, BUILTINS
from build_diagnostic_initramfs import archive


class GadgetPrerequisites(unittest.TestCase):
    def package(self):
        return archive([(n, 0o040755, b'', (0, 0)) for n in ['dev', 'proc', 'sys']] +
                       [('dev/console', 0o020600, b'', (5, 1)), ('init', 0o100755, b'test', (0, 0))])

    def test_modular_provider_build_and_builtin_symbols_do_not_admit_transport(self):
        states = config_states((ROOT / 'evidence/usb-gadget-prerequisites/resolved-gadget.config').read_text())
        result = audit(states, archive_inventory(self.package()))
        self.assertEqual(result['non_builtin_required_symbols'],
                         {n: 'm' for n in ['USB_CONFIGFS', 'USB_LIBCOMPOSITE', 'USB_F_ACM', 'USB_U_SERIAL']})
        states.update({n: 'y' for n in BUILTINS})
        result = audit(states, archive_inventory(self.package()))
        self.assertEqual(result['non_builtin_required_symbols'], {})
        self.assertFalse(result['source_package_ready'])
        self.assertFalse(result['transport_qualified'])

    def test_malformed_config_or_changed_package_is_not_silently_accepted(self):
        for text in ['CONFIG_USB_GADGET=y\nCONFIG_USB_GADGET=y', 'CONFIG_USB_GADGET=maybe']:
            with self.assertRaises(ValueError): config_states(text)
        for data in [self.package()[:40], self.package()[:200], b'not cpio', self.package()+b'payload']:
            with self.assertRaises(ValueError): archive_inventory(data)
        for name in ['../bad', '/bad', 'init']:
            with self.assertRaises(ValueError):
                archive_inventory(archive([('init', 0o100755, b'x', (0, 0)), (name, 0o100755, b'x', (0, 0))]))
        entries = archive_inventory(self.package());entries['lib/modules/test.ko'] = {}
        with self.assertRaises(ValueError): audit({}, entries)

    def test_require_ready_rejects_current_package(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'init.cpio.gz';p.write_bytes(gzip.compress(self.package(), mtime=0))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_usb_gadget_prerequisites.py'),
                                     '--initramfs', str(p), '--require-ready'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('"transport_qualified": false', result.stdout)

    def test_actual_cached_controller_role_function_ignores_injected_phy_errors(self):
        source = (ROOT / 'evidence/usb-prerequisites/ack/mediatek.c').read_text()
        start = source.index('static int mtk_otg_switch_set(');brace = source.index('{', start)
        depth = 1;end = brace+1
        while depth:
            depth += (source[end] == '{') - (source[end] == '}');end += 1
        actual = source[start:end]
        code = r'''
#include <assert.h>
#include <stdint.h>
#include <errno.h>
typedef uint8_t u8;
enum usb_role {USB_ROLE_NONE,USB_ROLE_HOST,USB_ROLE_DEVICE};
enum phy_mode {PHY_MODE_USB_OTG,PHY_MODE_USB_HOST,PHY_MODE_USB_DEVICE};
#define OTG_STATE_A_WAIT_VRISE 10
#define OTG_STATE_B_IDLE 11
#define MUSB_DEVCTL 0
#define MUSB_DEVCTL_SESSION 1
struct otg {int state;};struct xceiv {struct otg *otg;};
struct musb {void *mregs;struct xceiv *xceiv;int mode;};
struct mtk_glue {struct musb *musb;enum phy_mode phy_mode;enum usb_role role;void *phy,*dev;};
static int error,on,off,set,invalid;
static u8 readb(void *p) {return *(u8 *)p;}
static int phy_power_on(void *p) {(void)p;on++;return error;}
static int phy_power_off(void *p) {(void)p;off++;return error;}
static int phy_set_mode(void *p,enum phy_mode mode) {(void)p;(void)mode;set++;return error;}
static void musb_writeb(void *p,int offset,u8 value) {((u8 *)p)[offset]=value;}
#define MUSB_HST_MODE(m) ((m)->mode=1)
#define MUSB_DEV_MODE(m) ((m)->mode=2)
#define dev_err(d,...) do {(void)(d);invalid++;}while(0)
''' + actual + r'''
int main(void) {
 u8 reg;struct otg otg={0};struct xceiv x={.otg=&otg};struct musb m={.mregs=&reg,.xceiv=&x};
 struct mtk_glue g={.musb=&m};
 for(int fail=0;fail<2;fail++)for(int from=0;from<3;from++)for(int to=0;to<3;to++) {
  g.role=from;reg=0xff;error=fail?-EIO:0;on=off=set=0;
  assert(mtk_otg_switch_set(&g,to)==0);
  assert(g.role==(enum usb_role)to);
  assert(set==(from!=to));
  assert(on==(from==USB_ROLE_NONE && to!=USB_ROLE_NONE));
  assert(off==(from!=USB_ROLE_NONE && to==USB_ROLE_NONE));
  if(from!=to && fail)assert(set==1); /* injected backend failure still returned success */
 }
 assert(mtk_otg_switch_set(&g,(enum usb_role)99)==-EINVAL && invalid==1);
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as d:
            c = Path(d) / 'role.c';exe = Path(d) / 'role';c.write_text(code)
            result = subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', str(c), '-o', str(exe)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run([str(exe)], check=True, timeout=5)
