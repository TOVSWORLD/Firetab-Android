import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from apply_usb_port import apply
LOCK=json.loads((ROOT/'projects/firetabs-android/kernel/usb-port/inputs.json').read_text())


def function(source,name):
    index=source.index(name+'(');start=source.rfind('\n',0,index)+1;brace=source.index('{',index);depth=1;end=brace+1
    while depth:
        if source[end]=='{':depth+=1
        elif source[end]=='}':depth-=1
        end+=1
    return source[start:end]


class USBPort(unittest.TestCase):
    def tree(self,root):
        target=root/LOCK['target'];target.parent.mkdir(parents=True)
        shutil.copyfile(ROOT/LOCK['original_source'],target)
        shutil.copyfile(ROOT/LOCK['helper_source'],target.parent/'phy-mtk-io.h')
        for part in LOCK.get('additional_patches',[]):
            dest=root/part['target'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/part['original_source'],dest)
        return target

    def test_actual_patch_preserves_generic_policy_and_descriptors(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=self.tree(root);old=target.read_text();apply(root,LOCK['ack_commit']);new=target.read_text()
            for name in ['u2_phy_instance_power_off','u2_phy_props_set']:
                self.assertEqual(function(old,name),function(new,name),name)
            guard='\tif (tphy->pdata->mt8163_usb2) {\n\t\tmt8163_hs_slew_measure_and_apply(tphy, instance);\n\t\treturn;\n\t}\n\n'
            self.assertEqual(function(new,'hs_slew_rate_calibrate').replace(guard,''),function(old,'hs_slew_rate_calibrate'))
            for data in re.findall(r'static const struct mtk_phy_pdata \w+ = \{.*?\n\};',old,re.S):self.assertIn(data,new)
            self.assertIn('instance->type != PHY_TYPE_USB2 || instance->index != 0',new)
            self.assertIn('retval = mt8163_usb2_validate_eye(child_np)',new)
            init_guard='\tif (tphy->pdata->mt8163_usb2)\n\t\tmt8163_usb2_apply_analog(instance, false);\n\telse\n\t'
            self.assertEqual(function(new,'u2_phy_instance_init').replace(init_guard,'').replace('\t\tmtk_phy_update_field','\tmtk_phy_update_field'),function(old,'u2_phy_instance_init'))
            on_guard='\tif (tphy->pdata->mt8163_usb2)\n\t\tmt8163_usb2_apply_analog(instance, true);\n'
            self.assertEqual(function(new,'u2_phy_instance_power_on').replace(on_guard,''),function(old,'u2_phy_instance_power_on'))
            with self.assertRaises(ValueError):apply(root,LOCK['ack_commit'])

    def test_wrong_revision_and_header_drift_fail_before_writes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=self.tree(root);before=target.read_bytes()
            with self.assertRaises(ValueError):apply(root,'wrong')
            header=target.parent/'phy-mtk-io.h';header.write_bytes(header.read_bytes()+b'\n')
            with self.assertRaises(ValueError):apply(root,LOCK['ack_commit'])
            self.assertEqual(target.read_bytes(),before)

    def test_actual_c_analog_bit_preservation_and_conflicting_properties_in_ram(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=self.tree(root);apply(root,LOCK['ack_commit']);source=target.read_text()
            code=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#define __iomem
#define BIT(n) (1U<<(n))
#define GENMASK(h,l) ((~0U>>(31-(h))) & (~0U<<(l)))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
typedef uint8_t u8; typedef uint32_t u32;
#define U3P_USBPHYACR6 0x18
#define U3P_USBPHYACR1 0x04
#define PA1_RG_VRT_SEL GENMASK(14,12)
#define PA1_RG_TERM_SEL GENMASK(10,8)
struct u2phy_banks {void *com;};
struct mtk_phy_instance {struct u2phy_banks u2_banks;};
struct device_node {int present[3];u32 values[3];int malformed,extra_cells;};
static int property(const char *name) {
 if(!strcmp(name,"mediatek,eye-vrt"))return 0;
 if(!strcmp(name,"mediatek,eye-term"))return 1;
 assert(!strcmp(name,"mediatek,eye-src"));return 2;
}
static bool of_property_read_bool(struct device_node *n,const char *name) {return n->present[property(name)];}
static int of_property_count_u32_elems(struct device_node *n,const char *name) {
 (void)name;return n->malformed?-EINVAL:n->extra_cells?2:1;
}
static int of_property_read_u32(struct device_node *n,const char *name,u32 *v) {
 if(n->malformed)return -EINVAL;
 *v=n->values[property(name)];return 0;
}
static u8 readb(void *p) {return *(u8 *)p;}
static void writeb(u8 v,void *p) {*(u8 *)p=v;}
static void mtk_phy_set_bits(void *p,u32 mask) {u32 v;memcpy(&v,p,4);v|=mask;memcpy(p,&v,4);}
''' + function(source,'mt8163_usb2_apply_analog')+'\n'+function(source,'mt8163_usb2_validate_eye')+r'''
int main(void) {
 unsigned char common[256];struct mtk_phy_instance instance={.u2_banks={.com=common}};
 for(unsigned int mode=0;mode<2;mode++)for(u32 state=0;state<65536;state++) {
  memset(common,0xa5,sizeof(common));u32 initial=0x5a5a0000|state;
  memcpy(common+0x18,&initial,4);memcpy(common+0x04,&initial,4);
  mt8163_usb2_apply_analog(&instance,mode);
  u32 rx,eye;memcpy(&rx,common+0x18,4);memcpy(&eye,common+0x04,4);
  assert(rx==((mode?(initial&~8U):initial)|6U));
  assert(eye==(initial|0x7700U));
  for(int i=0;i<256;i++)if(!(i>=4&&i<8)&&!(i>=0x18&&i<0x1c))assert(common[i]==0xa5);
 }
 struct device_node np={0};assert(mt8163_usb2_validate_eye(&np)==0);
 for(int p=0;p<2;p++)for(u32 value=0;value<=8;value++) {
  memset(&np,0,sizeof(np));np.present[p]=1;np.values[p]=value;
  assert(mt8163_usb2_validate_eye(&np)==(value==7?0:-EINVAL));
 }
 np=(struct device_node){.present={1,1,0},.values={7,7,0}};
 assert(mt8163_usb2_validate_eye(&np)==0);np.extra_cells=1;assert(mt8163_usb2_validate_eye(&np)==-EINVAL);np.extra_cells=0;np.malformed=1;assert(mt8163_usb2_validate_eye(&np)==-EINVAL);
 np=(struct device_node){.present={0,0,1}};assert(mt8163_usb2_validate_eye(&np)==-EINVAL);
 return 0;
}
'''
            c=root/'analog.c';exe=root/'analog';c.write_text(code)
            compiled=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],capture_output=True,text=True)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            subprocess.run([str(exe)],check=True,timeout=5)

    def test_actual_c_resource_errors_measurement_cleanup_and_fixed_byte_in_ram(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=self.tree(root);apply(root,LOCK['ack_commit']);source=target.read_text()
            constants='\n'.join(re.search(r'^#define '+name+r'\s+.*$',source,re.M)[0] for name in ['U3P_U2FREQ_FMCR0','U3P_U2FREQ_VALUE','U3P_U2FREQ_FMMONR1','P2F_USB_FM_VALID','P2F_RG_CYCLECNT','P2F_RG_MONCLK_SEL','P2F_RG_FREQDET_EN','P2F_RG_FRCK_EN','U3P_FM_DET_CYCLE_CNT'])
            code=r'''
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <errno.h>
#define __iomem
#define BIT(n) (1U<<(n))
#define GENMASK(h,l) ((~0U>>(31-(h))) & (~0U<<(l)))
#define FIELD_PREP(mask,val) ((u32)(val)<<__builtin_ctz(mask))
typedef uint8_t u8; typedef uint32_t u32;
struct mutex { int held, initialized; };
struct device { int unused; };
struct resource { unsigned long start,end; };
struct platform_device { struct device dev; };
struct u2phy_banks { void *fmreg,*com; };
struct mtk_phy_instance { struct u2phy_banks u2_banks; };
struct mtk_tphy { struct device *dev; void *u2_freq; struct mutex u2_freq_lock; };
static unsigned char freq[256], common[256];
static struct mutex *active_lock;
static int poll_error, reads, warnings, writes, map_error;
static u32 observed;
static struct resource *provided;
#define IORESOURCE_MEM 0x200
#define resource_size(r) ((r)->end-(r)->start+1)
#define IS_ERR(p) ((intptr_t)(p)<0 && (intptr_t)(p)>=-4095)
#define PTR_ERR(p) ((int)(intptr_t)(p))
static struct resource *platform_get_resource_byname(struct platform_device *p,int kind,const char *name)
{ (void)p;assert(kind==IORESOURCE_MEM);assert(!strcmp(name,"u2-frequency"));return provided; }
static int dev_err_probe(struct device *d,int error,const char *fmt,...)
{ (void)d;(void)fmt;return error; }
static void *devm_ioremap_resource(struct device *d,struct resource *r)
{ (void)d;(void)r;return map_error ? (void *)(intptr_t)-EBUSY : freq; }
static void mutex_init(struct mutex *m) {m->held=0;m->initialized=1;}
static void mutex_lock(struct mutex *m) {assert(m->initialized && !m->held);m->held=1;}
static void mutex_unlock(struct mutex *m) {assert(m->held);m->held=0;}
static void udelay(int us) {assert(us==1 && active_lock->held);}
static u8 readb(void *p) {assert(active_lock->held);return *(u8 *)p;}
static void writeb(u8 v,void *p) {assert(active_lock->held);*(u8 *)p=v;writes++;}
static u32 readl(void *p) {u32 v;assert(active_lock->held);if(p==freq+12){reads++;return observed;}assert(p==freq || p==freq+16);memcpy(&v,p,4);return v;}
static void writel(u32 v,void *p) {assert(active_lock->held && (p==freq || p==freq+16));memcpy(p,&v,4);writes++;}
static int fake_poll(void *p,u8 *v,int delay,int timeout)
{assert(active_lock->held && p==freq+16 && delay==10 && timeout==3000000);*v=poll_error?0:1;return poll_error;}
#define readb_poll_timeout(addr,val,cond,delay,timeout) fake_poll((addr),&(val),(delay),(timeout))
#define dev_warn_ratelimited(d,fmt,...) do { (void)(d);assert(!active_lock->held);warnings++; } while(0)
'''+constants+'\n'+function(source,'mt8163_hs_slew_measure_and_apply')+'\n'+function(source,'mt8163_usb2_map_frequency')+r'''
int main(void) {
 static struct platform_device p={0};static struct mtk_tphy t={.dev=&p.dev};
 static struct resource r={.start=0x11210f00,.end=0x11210fff};
 provided=NULL;assert(mt8163_usb2_map_frequency(&p,&t)==-EINVAL);
 provided=&r;r.end=r.start+15;assert(mt8163_usb2_map_frequency(&p,&t)==-EINVAL);
 r.end=r.start+255;r.start++;assert(mt8163_usb2_map_frequency(&p,&t)==-EINVAL);r.start--;map_error=1;assert(mt8163_usb2_map_frequency(&p,&t)==-EBUSY);
 map_error=0;assert(mt8163_usb2_map_frequency(&p,&t)==0 && t.u2_freq==freq && t.u2_freq_lock.initialized);
 active_lock=&t.u2_freq_lock;
 struct mtk_phy_instance inst={.u2_banks={.fmreg=freq,.com=common}};
 for(int test=0;test<4;test++) {
  memset(freq,0xaa,sizeof(freq));memset(common,0xff,sizeof(common));
  reads=warnings=writes=0;poll_error=test==2?-ETIMEDOUT:0;observed=test==1?0:test==3?UINT32_MAX:64;
  mt8163_hs_slew_measure_and_apply(&t,&inst);
  assert(!active_lock->held && common[0x15]==0x60 && writes==8);
  u32 count;memcpy(&count,freq,4);assert((count&0xffffff)==1024 && !(count&(BIT(24)|GENMASK(27,26))));
  assert(freq[0x11]==0xaa);
  assert(reads==(poll_error?0:1));assert(warnings==!!(poll_error||!observed));
  for(int i=0;i<256;i++)if(i!=0x15)assert(common[i]==0xff);
 }
 return 0;
}
'''
            c=root/'test.c';exe=root/'test';c.write_text(code)
            compiled=subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],capture_output=True,text=True)
            self.assertEqual(compiled.returncode,0,compiled.stderr)
            subprocess.run([str(exe)],check=True,timeout=5)
