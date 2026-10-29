from pathlib import Path
import sys,re,json,tempfile,subprocess
sys.path.insert(0,'scripts');from audit_disp_pwm_source import function
R=Path(__file__).resolve().parents[1];E=R/'evidence/disp-pwm-source';P=R/'projects/firetabs-android/kernel/pwm-port'
from apply_pwm_port import apply
def run():
 with tempfile.TemporaryDirectory(prefix='pwm-native-') as temporary:
  tmp=Path(temporary);tree=tmp/'source';tree.mkdir();lock=json.loads((P/'inputs.json').read_text())
  for row in lock['files']+lock['build_inputs']:
   if 'original_sha256' in row and row['original_sha256'] is None:continue
   dest=tree/row['target'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((R/row['source']).read_bytes())
  apply(tree,lock['ack_commit']);return native(tree,tmp)

def native(tree,tmp):
 s=(tree/'drivers/pwm/pwm-mtk-disp.c').read_text();source=(E/'ack-pwm-mtk-disp.c').read_text();core=(E/'ack-core.c').read_text();legacy=(E/'legacy-ddp_pwm.c').read_text();header=(E/'ack-pwm.h').read_text();defs=(R/'evidence/mipi-source/legacy-ddp_reg.h').read_text()
 prefix=(E/'ram.c.in').read_text().split('/* ACTUAL_SOURCE */')[0]
 prefix=prefix.replace('struct device {int unused;};','struct mutex {int held;};struct device_node {int unused;};struct device {struct device_node *of_node;};')
 structs=s[s.index('struct mtk_pwm_data {'):s.index('static int mtk_disp_pwm_apply(')];structs+=re.search(r'struct pwm_state \{.*?\n};',header,re.S).group();prefix=prefix.replace('/* ACTUAL_STRUCTS */',structs)
 prefix=prefix.replace('static u32 regs[64];','static u32 log_offset[64],log_value[64];static bool log_cache[64],enforce_power;static u32 regs[64];')
 prefix=prefix.replace('return regs[slot(p)];','if(enforce_power&&mdp.data&&mdp.data->mt8163_strict)assert(mdp.strict_main_owned&&mdp.strict_mm_owned);return regs[slot(p)];')
 prefix=prefix.replace('unsigned o=slot(p);regs[o]=v;writes++;','unsigned o=slot(p);if(enforce_power&&mdp.data&&mdp.data->mt8163_strict)assert(mdp.strict_main_owned&&mdp.strict_mm_owned);assert(writes<64);log_offset[writes]=o*4;log_value[writes]=v;log_cache[writes]=mdp.enabled;regs[o]=v;writes++;')
 prefix=prefix.replace('return step()?ERR_PTR(-ENOMEM):&chip;','if(step())return ERR_PTR(-ENOMEM);memset(&mdp,0,sizeof(mdp));return &chip;')
 # Delay publication callback mock until after helpers and the core prototype.
 old=re.search(r'static int devm_pwmchip_add\([^\n]*',prefix).group();prefix=prefix.replace(old,'static int devm_pwmchip_add(struct device *,struct pwm_chip *);')
 constants='\n'.join(x for x in s.splitlines() if x.startswith('#define '))+'\n'+'\n'.join(x for x in defs.splitlines() if re.match(r'#define DISP_PWM_(?:EN|COMMIT|CON_0|CON_1)_OFF',x))
 code=constants+'\n'+s[s.index('static int mtk_disp_pwm_apply('):s.index('static inline struct mtk_disp_pwm')]+'\n'+(R/'evidence/pwm-kernel-integration/ram-extra.c.in').read_text()+'\n'
 code+='static int devm_pwmchip_add(struct device *d,struct pwm_chip *c){assert(d==&pdev.dev&&c==&chip);if(add_apply){struct pwm_state state={.period=1024,.duty_cycle=512,.enabled=true};assert(__pwm_apply(&pwm,&state)==0);}return step()?-EIO:0;}\n'
 for name in ['to_mtk_disp_pwm','mtk_disp_pwm_update_bits','mtk_disp_pwm_apply_legacy','mtk_disp_pwm_get_state_legacy']:code+=function(s,name)+'\n'
 code+=re.search(r'static const struct pwm_ops mtk_disp_pwm_ops = \{.*?\n};',s,re.S).group()+'\n'+function(s,'mtk_disp_pwm_probe_legacy')+'\n'
 code+=(tree/'drivers/pwm/mtk_pwm_mt8163.h').read_text()+'\n'
 for name in ['mt8163_pwm_data','mt8173_pwm_data','mt2701_pwm_data','mt8183_pwm_data']:code+=re.search(r'static const struct mtk_pwm_data '+name+r' = \{.*?\n};',s,re.S).group()+'\n'
 for name in ['pwm_state_valid','__pwm_apply']:code+=function(core,name)+'\n'
 for name in ['disp_pwm_config_init','disp_pwm_is_enabled','disp_pwm_set_drverIC_en','disp_pwm_set_enabled','disp_pwm_level_remap','disp_pwm_set_backlight_cmdq','ddp_pwm_power_on','ddp_pwm_power_off']:code+=function(legacy,name)+'\n'
 code=prefix+code+(R/'evidence/pwm-kernel-integration/ram-cases.c.in').read_text();c=tmp/'ram.c';binary=tmp/'ram';c.write_text(code)
 r=subprocess.run(['cc','-std=gnu11','-Wall','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
 if r.returncode:raise ValueError(r.stderr)
 subprocess.run([str(binary)],check=True)
 return {'native_passed':True,'register_states':65536,'old_descriptors':3,'probe_failure_stages':6,'kernel_build_passed':False,'runtime_qualified':False}

if __name__=="__main__":print(json.dumps(run(),indent=2))
