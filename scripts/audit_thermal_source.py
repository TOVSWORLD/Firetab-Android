#!/usr/bin/env python3
"""Finite source-only MT8163 thermal comparison; never admit a variant or sensor."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/thermal-source'


def function(source,name):
    match=re.search(r'^static (?:int|void|S32) '+name+r'\(',source,re.M)
    if not match:raise ValueError('Missing actual source function '+name)
    brace=source.index('{',match.start());end=brace+1;depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[match.start():end]


def audit():
    receipt=json.loads((E/'sources.json').read_text())
    for path,expected in receipt['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:raise ValueError('Thermal source input drift: '+path)
    ack=(E/'ack-auxadc_thermal.c').read_text();donor=(E/'donor-auxadc_thermal.c').read_text();legacy=(E/'legacy-mtk_thermal.c').read_text();devinfo=(E/'legacy-devinfo.c').read_text()
    if '"mediatek,mt8163-thermal"' in ack:raise ValueError('ACK match premise changed')
    if '"mediatek,mt8163-thermal"' not in donor:raise ValueError('Donor match missing')
    for anchor in ['"atag,devinfo"','g_devinfo_data[i] = tags->data[i]','ret = g_devinfo_data[index]']:
        if anchor not in devinfo:raise ValueError('Legacy calibration lineage changed')
    cal=function(legacy,'thermal_cal_prepare')
    for anchor in ['temp0 = get_devinfo_with_index(8)','temp1 = get_devinfo_with_index(7)','temp2 = get_devinfo_with_index(9)']:
        if anchor not in cal:raise ValueError('Legacy calibration word order changed')
    # Candidate buffer offset is a declaration, not proven atag word identity.
    dts=(ROOT/'evidence/dtb-compile/inputs/arch/arm64/boot/dts/mediatek/mt8163.dtsi').read_text()
    if not re.search(r'thermal_calibration: calib@100\s*\{\s*reg = <0x100 0xc>',dts):raise ValueError('Candidate calibration cell changed')
    prefix=r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
#include <stddef.h>
typedef int32_t S32; typedef uint32_t U32; typedef uint32_t u32;
#define BIT(n) (1U<<(n))
#define tscpu_dprintk(...) ((void)0)
static void mtkts_dump_cali_info(void) {}
static u32 words[3];
static u32 get_devinfo_with_index(unsigned n) { assert(n>=7 && n<=9); return words[n-7]; }
'''
    globals_=sorted(set(re.findall(r'\bg_\w+',re.sub(r'/\*.*?\*/|"(?:\\.|[^"\\])*"','',cal,flags=re.S))))
    code=prefix+'\nstatic S32 '+','.join(globals_)+';\n'+cal+'\n'
    macros='\n'.join(line for line in ack.splitlines() if line.startswith('#define CALIB_BUF') and '_V1' in line)
    code+=r'''
enum {VTS1,VTS2,VTS3,VTS4,VTS5,VTSABB};
struct conf {int num_sensors; const int *vts_index; int num_banks;};
struct mtk_thermal;
struct mtk_thermal_bank {struct mtk_thermal *mt;int id;};
struct mtk_thermal {struct conf *conf; int adc_ge,adc_oe,degc_cali,o_slope,vts[6];struct mtk_thermal_bank banks[3];};
'''+macros+'\n'+function(ack,'mtk_thermal_extract_efuse_v1')+'\n'
    # Actual callbacks with bank-temperature/locking replaced by RAM callbacks.
    code+=r'''
struct thermal_zone_device {void *priv;};
static void *thermal_zone_device_priv(struct thermal_zone_device *tz){return tz->priv;}
static unsigned locks,unlocks;
static void mtk_thermal_get_bank(struct mtk_thermal_bank *b){assert(b->id>=0 && b->id<3);locks++;}
static void mtk_thermal_put_bank(struct mtk_thermal_bank *b){(void)b;unlocks++;}
static int mtk_thermal_bank_temperature(struct mtk_thermal_bank *b){return (b->id+1)*10000;}
#define INT_MIN (-2147483647-1)
#define max(a,b) ((a)>(b)?(a):(b))
'''
    code+=function(ack,'mtk_read_temp').replace('mtk_read_temp(', 'ack_read_temp(',1)+'\n'
    code+=function(donor,'mtk_read_temp').replace('mtk_read_temp(', 'donor_read_temp(',1)+'\n'
    # Capture exact legacy mux writes into virtual slots, never MMIO addresses.
    code+=r'''
enum {TEMPADCPNP0,TEMPADCPNP1,TEMPADCPNP2,TEMPADCPNP3,TEMPPNPMUXADDR,TEMPADCWRITECTRL};
#define TS_CON1_P 123
static unsigned slots[6];
static void write_slot(unsigned value,unsigned slot){assert(slot<6);slots[slot]=value;}
#define THERMAL_WRAP_WR32(v,s) write_slot(v,s)
'''
    for i in range(3):code+=function(legacy,'thermal_config_Bank'+str(i)+'_TS')+'\n'
    defines='\n'.join(x for x in donor.splitlines() if x.startswith('#define MT8163_'))
    table=re.search(r'static const int mt8163_bank_data\[.*?\n};',donor,re.S).group()
    mux=re.search(r'static const int mt8163_mux_values\[.*?;',donor,re.S).group()
    code+=defines+'\n'+table+'\n'+mux+'\n'
    code+=r'''
int main(void) {
 static const int vts[]={VTS1,VTS2,VTS3};struct conf c={3,vts,3};struct mtk_thermal mt={.conf=&c};unsigned differences=0;
 for(unsigned id=0;id<2;id++)for(unsigned sign=0;sign<2;sign++)for(unsigned slope=0;slope<64;slope++){
  words[0]=1U|(40U<<1)|(260U<<17)|(260U<<8)|(sign<<7)|(slope<<26);
  words[1]=(512U<<22)|(512U<<12)|260U|(id<<9);words[2]=0;
  thermal_cal_prepare();assert(mtk_thermal_extract_efuse_v1(&mt,words)==0);
  assert(mt.adc_ge==g_adc_ge_t && mt.degc_cali==g_degc_cali);
  assert(mt.vts[0]==g_o_vtsmcu1 && mt.vts[1]==g_o_vtsmcu2 && mt.vts[2]==g_o_vtsmcu3);
  int legacy_slope=g_o_slope_sign?-g_o_slope:g_o_slope;
  if(legacy_slope!=mt.o_slope)differences++;
 }
 assert(differences==126);words[0]=0;assert(mtk_thermal_extract_efuse_v1(&mt,words)==-EINVAL);thermal_cal_prepare();assert(g_adc_ge_t==512 && g_adc_oe_t==512 && g_degc_cali==40 && g_o_slope==0);
 for(int bank=0;bank<3;bank++){mt.banks[bank].mt=&mt;mt.banks[bank].id=bank;}
 struct thermal_zone_device tz={&mt};int t=0;assert(ack_read_temp(&tz,&t)==0 && t==30000);assert(locks==3 && unlocks==3);
 for(int bank=0;bank<3;bank++){tz.priv=&mt.banks[bank];assert(donor_read_temp(&tz,&t)==0 && t==(bank+1)*10000);}assert(locks==6 && unlocks==6);
 thermal_config_Bank0_TS();assert(slots[0]==0 && slots[1]==1);
 thermal_config_Bank1_TS();assert(slots[0]==2 && slots[1]==16);
 thermal_config_Bank2_TS();assert(slots[0]==3 && slots[1]==1 && slots[2]==2 && slots[3]==16);
 assert(mt8163_mux_values[mt8163_bank_data[0][0]]==0 && mt8163_mux_values[mt8163_bank_data[0][1]]==1);
 assert(mt8163_mux_values[mt8163_bank_data[1][0]]==1); /* differs legacy bank1 first mux2 */
 assert(mt8163_mux_values[mt8163_bank_data[2][0]]==0); /* differs legacy bank2 first mux3 */
 printf("{\"synthetic_calibration_cases\":256,\"signed_slope_differences\":%u,\"callback_cases\":4,\"legacy_mux_banks\":3}\n",differences);
 return 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        c=Path(tmp)/'audit.c';binary=Path(tmp)/'audit';c.write_text(code)
        r=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
        if r.returncode:raise ValueError('Actual C RAM compilation failed: '+r.stderr)
        result=json.loads(subprocess.check_output([str(binary)],text=True))
    return {'scope':'Actual C source/RAM comparisons, not thermal measurements or equivalent hardware behavior','passed':True,'c_controls':result,'legacy_devinfo_indices':[7,8,9],'candidate_nvmem_offset':256,'candidate_nvmem_bytes':12,'atag_to_nvmem_identity_proven':False,'donor_changes_existing_soc_callback_contract':True,'donor_bank_table_matches_active_legacy_mux_writes':False,'thermal_source_port_admitted':False,'binding_match_admitted':False,'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();result=audit()
    if args.check:
        if result!=json.loads((E/'result.json').read_text()):raise ValueError('Thermal result drift')
    else:(E/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
