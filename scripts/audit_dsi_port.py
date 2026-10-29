from pathlib import Path
import sys, tempfile, subprocess, json, hashlib, re
sys.path.insert(0,'scripts')
from audit_dsi_source import function
R=Path(__file__).resolve().parents[1];E=R/'evidence/dsi-source';P=R/'projects/firetabs-android/kernel/dsi-port'
from apply_dsi_port import apply
def run():
 with tempfile.TemporaryDirectory(prefix='dsi-native-') as tmp:
  tree=Path(tmp)/'source';tree.mkdir()
  lock=json.loads((P/'inputs.json').read_text())
  for part in lock['files']+lock['build_inputs']:
   if 'original_sha256' in part and part['original_sha256'] is None:continue
   dest=tree/part['target'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((R/part['source']).read_bytes())
  apply(tree,lock['ack_commit'])
  return native(tree,Path(tmp))

def native(tree,tmp):
 s=(tree/'drivers/gpu/drm/mediatek/mtk_dsi.c').read_text();prefix=(E/'ram.c.in').read_text().split('/* ACTUAL_SOURCE */')[0]
 # Reuse RAM callbacks, with the actual enlarged private state and packet layout.
 prefix=prefix.replace('typedef uint32_t u32;typedef uint8_t u8;','typedef uint32_t u32;typedef uint8_t u8;typedef uint64_t u64;typedef int32_t s32;typedef int irqreturn_t;\n#include <limits.h>\n#include <sys/types.h>\nstruct mutex {int held;};typedef int spinlock_t;enum mipi_dsi_pixel_format { RAM_FORMAT=0 };')
 prefix=prefix.replace('size_t tx_len;const void *tx_buf;','size_t tx_len;const void *tx_buf;size_t rx_len;void *rx_buf;')
 prefix=prefix.replace('support_per_frame_lp,bypass_rack,no_vm_done_irq','support_per_frame_lp,mt8163_strict,bypass_rack,no_vm_done_irq')
 a=prefix.index('struct mtk_dsi {');b=prefix.index('\nstatic struct mtk_dsi dsi;',a)
 struct=s[s.index('struct mtk_dsi {'):s.index('\n};',s.index('struct mtk_dsi {'))+3]
 struct=struct.replace('struct videomode vm;','struct {uint64_t pixelclock;} vm;').replace('struct mtk_phy_timing phy_timing;','int phy_timing;').replace('wait_queue_head_t irq_wait_queue;','int irq_wait_queue;').replace('struct drm_connector *connector;','void *connector;')
 prefix=prefix[:a]+struct+prefix[b:]
 # Actual wrappers replace these baseline stub definitions.
 import re
 for name in ['mtk_dsi_set_interrupt_enable','mtk_output_dsi_enable','mtk_dsi_irq']:
  prefix=re.sub(r'static (?:void|int) '+name+r'\([^{}]*\)\{[^{}]*\}', '',prefix)
 prefix=prefix.replace(' && !flags && name',' && flags==IRQF_NO_AUTOEN && name')
 prefix=prefix.replace('static const char *dev_name','static irqreturn_t mtk_dsi_irq(int,void *);\nstatic const char *dev_name')
 prefix=prefix.replace('#define IRQF_TRIGGER_NONE 0','#define IRQF_TRIGGER_NONE 0\n#define IRQF_NO_AUTOEN 1')
 prefix=prefix.replace('return fail_bpp?-EINVAL:24','return fail_bpp||f<0?-EINVAL:24')
 # Include the actual pinned protocol/controller constants.
 donor=s;defs='\n'.join(re.findall(r'^#define (?:[^\n]*\\\n)*[^\n]*',donor[:donor.index('struct mtk_phy_timing')],re.M))
 enums='\n'.join(re.findall(r'^enum(?:\s+\w+)?\s*\{.*?^};',(E/'mipi_display.h').read_text(),re.M|re.S))
 flags='\n'.join(x for x in (E/'drm_mipi_dsi.h').read_text().splitlines() if x.startswith('#define MIPI_DSI_MSG_'))
 code=prefix+'\n'+defs+'\n'+enums+'\n'+flags+'\n'+(R/'evidence/dsi-kernel-integration/ram-support.c.in').read_text()+'\n'
 for name in ['mtk_dsi_set_interrupt_enable','mtk_dsi_irq_data_set','mtk_dsi_irq_data_clear','mtk_dsi_irq','mtk_dsi_switch_to_cmd_mode','mtk_dsi_poweron','mtk_dsi_poweroff','mtk_output_dsi_enable','mtk_dsi_bind','mtk_dsi_unbind','mtk_dsi_host_attach','mtk_dsi_host_detach','mtk_dsi_cmdq','mtk_dsi_host_transfer','mtk_dsi_probe','mtk_dsi_remove']:
  code+=function(s,name+'_legacy')+'\n' if name in ['mtk_dsi_poweron','mtk_dsi_bind','mtk_dsi_unbind','mtk_dsi_host_attach','mtk_dsi_host_detach','mtk_dsi_cmdq'] else ''
 code+=(tree/'drivers/gpu/drm/mediatek/mtk_dsi_mt8163.h').read_text()+'\n'
 for name in ['mtk_dsi_bridge_atomic_pre_enable','mtk_dsi_bridge_atomic_enable','mtk_dsi_bridge_atomic_disable','mtk_dsi_bridge_atomic_post_disable']:
  code+=function(s,name)+'\n'
 for name in ['mtk_dsi_ddp_start','mtk_dsi_ddp_stop']:
  code+=function(s.replace('void '+name+'(', 'static void '+name+'(',1),name)+'\n'
 code+=(R/'evidence/dsi-kernel-integration/ram-cases.c.in').read_text()
 c=tmp/'ram.c';binary=tmp/'ram';c.write_text(code)
 result=subprocess.run(['cc','-std=gnu11','-Wall','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
 if result.returncode:raise ValueError(result.stderr)
 subprocess.run([str(binary)],check=True)
 return {'native_passed':True,'runtime_qualified':False,'maximum_payload':248,'queue_count_mask':63,'kernel_build_passed':False}

if __name__=="__main__":print(json.dumps(run(),indent=2))
