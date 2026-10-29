#!/usr/bin/env python3
"""Finite MIPI source/RAM comparison; does not qualify PHY or display operation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'evidence/mipi-source'


def function(source,name):
    match=re.search(r'^(?:static )?(?:int|long|unsigned long|void) '+name+r'\(',source,re.M)
    if not match:raise ValueError('Missing source function '+name)
    brace=source.index('{',match.start());end=brace+1;depth=1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[match.start():end]


def audit():
    sources=json.loads((E/'sources.json').read_text())
    for path,expected in sources['sha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:raise ValueError('MIPI source input drift: '+path)
    ack=(E/'phy-mtk-mipi-dsi-mt8173.c').read_text();donor=(E/'donor-phy-mtk-mipi-dsi-mt8173.c').read_text();generic=(E/'phy-mtk-mipi-dsi.c').read_text();dg=(E/'donor-phy-mtk-mipi-dsi.c').read_text();legacy=(E/'legacy-ddp_dsi.c').read_text();header=(E/'legacy-ddp_reg.h').read_text()
    if '"mediatek,mt8163-mipi-tx"' in generic or '"mediatek,mt8163-mipi-tx"' not in dg:raise ValueError('MIPI match premise changed')
    if 'device_reset_optional(dev)' not in dg or 'device_reset_optional(dev)' in generic:raise ValueError('Donor global reset boundary changed')
    for anchor in ['pcw = data_Rate * txdiv / 13','RG_MPPLL_PRESERVE, 2','RG_DSI0_MPPLL_SDM_PCW_CHG, 0','RG_DSI0_MPPLL_SDM_PCW_CHG, 1']:
        if anchor not in legacy:raise ValueError('Legacy active PLL contract changed')
    struct=re.search(r'struct MIPITX_DSI_PLL_TOP_REG \{.*?\n};',header,re.S).group()
    if 'RG_MPPLL_PRESERVE:8' not in struct:raise ValueError('Legacy preserve field changed')
    if 'static long mtk_mipi_tx_pll_round_rate(' in donor:raise ValueError('Donor missing-callback premise changed')
    prepare=function(donor,'mtk_mipi_tx_pll_prepare_mt8163');unprepare=function(ack,'mtk_mipi_tx_pll_unprepare');round_rate=function(ack,'mtk_mipi_tx_pll_round_rate')
    ops=re.search(r'static const struct clk_ops mtk_mipi_tx_pll_ops_mt8163 = \{.*?\n};',donor,re.S).group()
    constants=donor[donor.index('#define MIPITX_DSI_CON'):donor.index('static int mtk_mipi_tx_pll_prepare(')]
    io='\n'.join(x for x in (E/'phy-mtk-io.h').read_text().splitlines() if not x.startswith('#include'))
    prefix=r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint32_t u32;typedef uint64_t u64;typedef uint8_t u8;
#define __iomem
#define BIT(n) (1U<<(n))
#define GENMASK(h,l) ((~0U>>(31-(h))) & (~0U<<(l)))
#define FIELD_PREP(m,v) (((u32)(v)<<__builtin_ctz((u32)(m)))&(m))
#define BUILD_BUG_ON_MSG(c,m) _Static_assert(!(c),m)
#define dev_dbg(...) ((void)0)
#define clamp_val(v,l,h) ((v)<(l)?(l):(v)>(h)?(h):(v))
struct mtk_mipi_tx;
struct clk_hw {struct mtk_mipi_tx *owner;};
struct mtk_mipitx_data {u32 mppll_preserve;};
struct mtk_mipi_tx {void *regs;u32 data_rate;void *dev;const struct mtk_mipitx_data *driver_data;};
static u32 regs[27];static unsigned writes,reads,delays,chg_count;static u32 chg[2];
static unsigned slot(void *p){uintptr_t d=(uintptr_t)p-(uintptr_t)regs;assert(d<sizeof(regs) && !(d&3));return d/4;}
static u32 readl(void *p){reads++;return regs[slot(p)];}
static void writel(u32 v,void *p){unsigned i=slot(p);writes++;regs[i]=v;if(i==0x60/4 && chg_count<2)chg[chg_count++]=v;}
static void usleep_range(unsigned l,unsigned h){assert((l==20 || l==30) && h==100);delays++;}
static u64 div_u64(u64 n,u32 d){assert(d);return n/d;}
static struct mtk_mipi_tx *mtk_mipi_tx_from_clk_hw(struct clk_hw *hw){return hw->owner;}
struct clk_ops {int (*prepare)(struct clk_hw *);void (*unprepare)(struct clk_hw *);long (*round_rate)(struct clk_hw *,unsigned long,unsigned long *);int (*set_rate)(struct clk_hw *,unsigned long,unsigned long);unsigned long (*recalc_rate)(struct clk_hw *,unsigned long);};
'''
    code=prefix+constants+'\n'+io+'\n'+prepare+'\n'+unprepare+'\n'+function(generic,'mtk_mipi_tx_pll_set_rate')+'\n'+function(generic,'mtk_mipi_tx_pll_recalc_rate')+'\n'
    main=r'''
static void reset_ram(void){memset(regs,0,sizeof(regs));writes=reads=delays=chg_count=0;}
int main(void){
 assert(sizeof(struct MIPITX_DSI_PLL_TOP_REG)==4);
 struct mtk_mipitx_data data={2};struct mtk_mipi_tx mt={.regs=regs,.driver_data=&data};struct clk_hw hw={&mt};unsigned long ref=26000000;
 unsigned matches=0;
 for(unsigned initial=0;initial<65536;initial++){
  reset_ram();mt.data_rate=500000000;regs[0x64/4]=initial;assert(mtk_mipi_tx_pll_ops_mt8163.prepare(&hw)==0);
  struct MIPITX_DSI_PLL_TOP_REG bits;u32 legacy_word=initial;memcpy(&bits,&legacy_word,4);bits.RG_MPPLL_PRESERVE=2;memcpy(&legacy_word,&bits,4);
  if(regs[0x64/4]==legacy_word)matches++;
 }
 assert(matches==8192);
 for(unsigned mhz=50;mhz<=1250;mhz++){
  unsigned div=mhz>=500?1:mhz>=250?2:mhz>=125?4:mhz>62?8:16;
  unsigned product=mhz*div,rem=product%13;
  u32 expected=((product/13)&127)<<24 | ((256*rem/13)&255)<<16 | ((256*(256*rem%13)/13)&255)<<8 | ((256*(256*(256*rem%13)%13)/13)&255);
  reset_ram();mt.data_rate=mhz*1000000;assert(mtk_mipi_tx_pll_ops_mt8163.prepare(&hw)==0);assert(regs[0x58/4]==expected);assert(delays==3);assert(chg_count==2 && !(chg[0]&1) && (chg[1]&1));
 }
 reset_ram();mt.data_rate=49999999;assert(mtk_mipi_tx_pll_ops_mt8163.prepare(&hw)==-EINVAL && !writes && !reads && !delays);
 reset_ram();mt.data_rate=1250000001;assert(mtk_mipi_tx_pll_ops_mt8163.prepare(&hw)==0 && writes);assert(mtk_mipi_tx_pll_ops_mt8163.round_rate(&hw,1250000001,&ref)==1250000000);
 reset_ram();regs[0x64/4]=0x8000;mt.data_rate=500000000;assert(mtk_mipi_tx_pll_ops_mt8163.prepare(&hw)==0);assert(regs[0x64/4]&0x8000);mtk_mipi_tx_pll_ops_mt8163.unprepare(&hw);assert(!(regs[0x64/4]&0x8000));
 assert(mtk_mipi_tx_pll_ops_mt8163.set_rate(&hw,123456789,ref)==0);assert(mtk_mipi_tx_pll_ops_mt8163.recalc_rate(&hw,ref)==123456789);
 printf("{\"low16_preserve_states\":65536,\"legacy_donor_equal_states\":%u,\"integer_mhz_pcw_cases\":1201,\"below_min_no_io\":true,\"donor_prepare_above_round_max_accepts\":true,\"generic_unprepare_clears_outside_donor_field\":true}\n",matches);
 return 0;
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        c=Path(tmp)/'mipi.c';c.write_text(code+ops)
        negative=subprocess.run(['cc','-std=gnu11','-fsyntax-only',str(c)],capture_output=True,text=True)
        if not negative.returncode or 'mtk_mipi_tx_pll_round_rate' not in negative.stderr:raise ValueError('Missing donor callback negative control changed')
        c.write_text(code+round_rate+'\n'+ops+'\n'+struct+'\n'+main);binary=Path(tmp)/'mipi'
        result=subprocess.run(['cc','-std=gnu11','-Wall','-Werror','-fsanitize=address,undefined',str(c),'-o',str(binary)],capture_output=True,text=True)
        if result.returncode:raise ValueError('Actual C RAM compile failed: '+result.stderr)
        controls=json.loads(subprocess.check_output([str(binary)],text=True))
    return {'scope':'Actual selected C and isolated little-endian register/PCW model; no physical samples or whole-sequence equivalence','passed':True,'controls':controls,'donor_round_rate_reference_undefined_in_pinned_file':True,'donor_globally_adds_optional_reset':True,'legacy_preserve_bits':[7,14],'donor_preserve_bits':[7,11],'existing_unprepare_preserve_bits':[8,15],'prepare_required_extent_bytes':108,'pll_reference_formula_hz':26000000,'donor_delay_us_lower_bounds':[30,30,20],'legacy_delay_ms':1,'phy_binding_admitted':False,'runtime_qualified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();result=audit()
    if args.check:
        if result!=json.loads((E/'result.json').read_text()):raise ValueError('MIPI audit result drift')
    else:(E/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
