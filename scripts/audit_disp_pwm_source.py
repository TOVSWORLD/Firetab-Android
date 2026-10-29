#!/usr/bin/env python3
"""Execute pinned actual PWM/core/legacy C in RAM; never admit a PWM variant."""
import argparse,hashlib,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'evidence/disp-pwm-source'
def function(s,name):
 m=re.search(r'^(?:static )?(?:inline )?[\w *]+\b'+name+r'\([^;{]*\)\n\{',s,re.M)
 if not m:raise ValueError('Missing actual PWM function '+name)
 end=s.index('{',m.start())+1;depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]
def audit():
 lock=json.loads((E/'sources.json').read_text())
 for path,sha in lock['sha256'].items():
  if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=sha:raise ValueError('Reviewed PWM input drift: '+path)
 source=(E/'ack-pwm-mtk-disp.c').read_text();legacy=(E/'legacy-ddp_pwm.c').read_text();core=(E/'ack-core.c').read_text();header=(E/'ack-pwm.h').read_text();defs=(ROOT/'evidence/mipi-source/legacy-ddp_reg.h').read_text()
 if (E/'donor-pwm-mtk-disp.c').read_bytes()!=(E/'ack-pwm-mtk-disp.c').read_bytes():raise ValueError('Donor equivalence premise changed')
 assert 'mediatek,mt8163-disp-pwm' not in source
 graph=json.loads((ROOT/'evidence/dsi-binding/captured-graph.json').read_text())['nodes'];node=graph['/soc/pwm@14014000'];assert node['status']==['okay'] and node['clocks']==[40,33,40,32] and node['power-domains']==[21,0]
 assert graph['/soc/syscon@14000000']['phandle']==[40] and graph['/soc/syscon@14000000']['#clock-cells']==[1]
 path=(E/'legacy-ddp_path.c').read_text();assert 'int ddp_module_clock_enable(MM_CLK_ENUM module, bool enable)' in path and 'return -1;' in function(path,'ddp_module_clock_enable')
 structs=source[source.index('struct mtk_pwm_data {'):source.index('static inline struct mtk_disp_pwm')]
 structs+=re.search(r'struct pwm_state \{.*?\n};',header,re.S).group()
 constants='\n'.join(x for x in source.splitlines() if x.startswith('#define '))+'\n'+'\n'.join(x for x in defs.splitlines() if re.match(r'#define DISP_PWM_(?:EN|COMMIT|CON_0|CON_1)_OFF',x))
 code=constants+'\n'
 for name in ['to_mtk_disp_pwm','mtk_disp_pwm_update_bits','mtk_disp_pwm_apply','mtk_disp_pwm_get_state']:code+=function(source,name)+'\n'
 code+=re.search(r'static const struct pwm_ops mtk_disp_pwm_ops = \{.*?\n};',source,re.S).group()+'\n'
 code+=function(source,'mtk_disp_pwm_probe')+'\n'+re.search(r'static const struct mtk_pwm_data mt8173_pwm_data = \{.*?\n};',source,re.S).group()+'\n'
 for name in ['pwm_state_valid','__pwm_apply']:code+=function(core,name)+'\n'
 for name in ['disp_pwm_config_init','disp_pwm_is_enabled','disp_pwm_set_drverIC_en','disp_pwm_set_enabled','disp_pwm_level_remap','disp_pwm_set_backlight_cmdq','ddp_pwm_power_on','ddp_pwm_power_off']:code+=function(legacy,name)+'\n'
 template=(E/'ram.c.in').read_text().replace('/* ACTUAL_STRUCTS */',structs).replace('/* ACTUAL_SOURCE */',code)
 with tempfile.TemporaryDirectory(prefix='pwm-source-') as tmp:
  c=Path(tmp)/'ram.c';binary=Path(tmp)/'ram';c.write_text(template);r=subprocess.run(['cc','-std=gnu11','-Wall','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
  if r.returncode:raise ValueError(r.stderr)
  subprocess.run([str(binary)],check=True)
 return {'scope':'Actual selected PWM/core/legacy C RAM witnesses,not installed behavior or hardware width proof','passed':True,'candidate_status':'okay','queued_disabled_lead_corrected':True,'candidate_main_clock_mmsys_id':33,'candidate_mm_clock_mmsys_id':32,'ack_donor_driver_byte_identical':True,'explicit_mt8163_match_present':False,'actual_core_accepts_disabled_irrelevant_parameters':True,'framework_valid_disabled_change_can_enable_from_cached_off':True,'framework_cache_disabled_driver_enabled_divergence':True,'get_state_raw_period_missing_encoded_plus_one':True,'raw_period_states_tested':4096,'u64_period_can_wrap_u32_divider_before_range_check':True,'wrap_period_ns':(1<<44)+1024,'wrapped_programmed_cycles_at_1GHz':1024,'rate_zero_apply_can_enable':True,'rate_zero_get_state_reaches_zero_divisor_callback_twice':True,'zero_divisor_helper_instrumented_not_kernel_division_executed':True,'clock_failure_cleanup_cases':2,'probe_failure_stages':5,'legacy_period_mask':1023,'modern_period_mask':4095,'modern_divider_mask':1023,'legacy_divider_mask':1023,'period_low_word_states':65536,'period_operation_equal':16384,'legacy_commit_full_word_modern_bit0_only':True,'commit_low_word_states':65536,'commit_operation_equal':2,'legacy_three_clock_order_and_discarded_errors_observed':True,'legacy_subset_not_hardware_width_proof':True,'kernel_variant_admitted':False,'binding_admitted':False,'runtime_qualified':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=audit()
 if a.check:
  if r!=json.loads((E/'result.json').read_text()):raise ValueError('PWM result drift')
 else:(E/'result.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
if __name__=='__main__':main()
