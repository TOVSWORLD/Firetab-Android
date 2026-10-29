/* Host-only template: tests inject actual patched functions. No device access. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;
enum usb_role {USB_ROLE_NONE,USB_ROLE_HOST,USB_ROLE_DEVICE};
enum phy_mode {PHY_MODE_USB_OTG,PHY_MODE_USB_HOST,PHY_MODE_USB_DEVICE};
#define MUSB_HOST 1
#define MUSB_PERIPHERAL 2
#define MUSB_OTG 3
#define MUSB_DEVCTL 0x60
#define MUSB_DEVCTL_SESSION 1
#define OTG_STATE_A_WAIT_VRISE 10
#define OTG_STATE_B_IDLE 11
#define MUSB_TXTOGEN 0x86
#define MUSB_RXTOGEN 0x82
#define MTK_TOGGLE_EN 0xffff
#define USB_L1INTM 0xa4
#define TX_INT_STATUS 1
#define RX_INT_STATUS 2
#define USBCOM_INT_STATUS 4
#define DMA_INT_STATUS 8
#define CONFIG_USB_INVENTRA_DMA 1
#define MUSB_HSDMA_INTR 0x200
#define DMA_INTR_STATUS_MSK 0xff
#define DMA_INTR_UNMASK_SET_MSK 0xff000000
#define MTK_MUSB_CLKS_NUM 3
struct device {struct device *parent;void *data;};
struct otg {int state;};struct xceiv {struct otg *otg;};
struct musb {struct device *controller;void *mregs,*phy;struct xceiv *xceiv;bool is_host;int (*isr)(int,void *);int mode,port_mode;};
struct mtk_glue {struct device *dev;struct musb *musb;void *phy;struct xceiv *xceiv;enum phy_mode phy_mode;enum usb_role role;int clks[3];bool strict_role_errors,role_faulted,role_ready,phy_initialized,phy_powered,role_switch_registered;};
struct usb_role_switch {struct mtk_glue *data;};
static unsigned char regs[1024];
static struct device parent,dev;static struct otg otg;static struct xceiv xceiv;static struct musb musb;static struct mtk_glue glue;
static int init_count,power_count,init_error,on_error,off_error,exit_error,mode_errors[4],mode_calls,registration_error;
static int irq_enables,register_writes,registered,unregistered,clocks_disabled,pm_put,pm_disabled,errors;
static char trace[64];static unsigned int trace_n;
static void record(char c) {assert(trace_n+1<sizeof(trace));trace[trace_n++]=c;trace[trace_n]=0;}
static int phy_init(void *p) {(void)p;record('I');if(init_error)return init_error;init_count++;return 0;}
static int phy_exit(void *p) {(void)p;record('E');assert(init_count>0 && power_count==0);if(exit_error)return exit_error;init_count--;return 0;}
static int phy_power_on(void *p) {(void)p;record('P');assert(init_count>0);if(on_error)return on_error;power_count++;return 0;}
static int phy_power_off(void *p) {(void)p;record('O');assert(power_count>0);if(off_error)return off_error;power_count--;return 0;}
static int phy_set_mode(void *p,enum phy_mode mode) {(void)p;(void)mode;record('M');assert(mode_calls<4);return mode_errors[mode_calls++];}
static void fake_dev_err(void *p,const char *fmt,...) {(void)p;(void)fmt;errors++;}
#define dev_err(...) fake_dev_err(__VA_ARGS__)
static void *dev_get_drvdata(struct device *d) {return d->data;}
static void *usb_role_switch_get_drvdata(struct usb_role_switch *s) {return s->data;}
static u8 readb(void *p) {return *(u8 *)p;}
static void musb_writeb(void *p,int offset,u8 v) {((u8 *)p)[offset]=v;register_writes++;}
static void musb_writew(void *p,int offset,u16 v) {memcpy((u8 *)p+offset,&v,2);register_writes++;}
static void musb_writel(void *p,int offset,u32 v) {memcpy((u8 *)p+offset,&v,4);register_writes++;if(offset==USB_L1INTM)irq_enables++;}
#define MUSB_HST_MODE(m) ((m)->mode=1)
#define MUSB_DEV_MODE(m) ((m)->mode=2)
static int mtk_musb_interrupt(int irq,void *p) {(void)irq;(void)p;return 0;}
static int mtk_otg_switch_init(struct mtk_glue *g) {(void)g;record('R');if(registration_error)return registration_error;registered++;return 0;}
static void mtk_otg_switch_exit(struct mtk_glue *g) {(void)g;record('U');unregistered++;}
static void clk_bulk_disable_unprepare(int n,int *clks) {(void)clks;assert(n==3);clocks_disabled++;}
static void pm_runtime_put_sync(struct device *d) {(void)d;pm_put++;}
static void pm_runtime_disable(struct device *d) {(void)d;pm_disabled++;}
/* ACTUAL_FUNCTIONS */
static void reset(enum usb_role role,bool powered,bool ready)
{
 memset(regs,0x5a,sizeof(regs));memset(&glue,0,sizeof(glue));memset(&musb,0,sizeof(musb));memset(&otg,0,sizeof(otg));
 parent.data=&glue;dev.parent=&parent;xceiv.otg=&otg;musb.controller=&dev;musb.mregs=regs;musb.xceiv=&xceiv;musb.port_mode=MUSB_OTG;
 glue.dev=&parent;glue.musb=&musb;glue.xceiv=&xceiv;glue.strict_role_errors=true;glue.role=role;glue.phy_mode=role==USB_ROLE_HOST?PHY_MODE_USB_HOST:role==USB_ROLE_DEVICE?PHY_MODE_USB_DEVICE:PHY_MODE_USB_OTG;
 glue.phy_powered=powered;glue.phy_initialized=ready;glue.role_ready=ready;init_count=ready;power_count=powered;
 init_error=on_error=off_error=exit_error=mode_calls=registration_error=0;memset(mode_errors,0,sizeof(mode_errors));
 irq_enables=register_writes=registered=unregistered=clocks_disabled=pm_put=pm_disabled=errors=0;trace_n=0;trace[0]=0;
}
static void fault_unchanged(enum usb_role before,enum phy_mode mode,const unsigned char *before_regs,int expected)
{
 struct usb_role_switch sw={.data=&glue};
 assert(glue.role==before && glue.phy_mode==mode && glue.role_faulted);
 assert(memcmp(regs,before_regs,sizeof(regs))==0 && register_writes==0);
 assert(musb_usb_role_sx_get(&sw)==USB_ROLE_NONE);
 unsigned int calls=trace_n;assert(musb_usb_role_sx_set(&sw,before)==-EIO && trace_n==calls);
 assert(mtk_musb_set_mode(&musb,before==USB_ROLE_HOST?MUSB_HOST:before==USB_ROLE_DEVICE?MUSB_PERIPHERAL:MUSB_OTG)==-EIO);
 assert(errors>=expected);
}
int main(void)
{
 unsigned char saved[sizeof(regs)];
 /* Twelve successful prior-power/target combinations, then idempotency. */
 for(int state=0;state<4;state++)for(int to=0;to<3;to++) {
  enum usb_role from=state<2?USB_ROLE_NONE:state==2?USB_ROLE_HOST:USB_ROLE_DEVICE;
  reset(from,state!=0,true);assert(mtk_otg_switch_set(&glue,to)==0);
  assert(glue.role==(enum usb_role)to && power_count==(to!=USB_ROLE_NONE));
  assert(glue.phy_powered==(to!=USB_ROLE_NONE) && !glue.role_faulted);
  if(from==USB_ROLE_NONE && state==1 && to!=USB_ROLE_NONE)assert(strchr(trace,'P')==NULL); /* init already owns power */
  unsigned int calls=trace_n;int writes=register_writes;assert(mtk_otg_switch_set(&glue,to)==0 && trace_n==calls && register_writes==writes);
 }
 reset(USB_ROLE_NONE,false,false);assert(mtk_otg_switch_set(&glue,USB_ROLE_DEVICE)==-EAGAIN && trace_n==0);
 assert(mtk_otg_switch_set(&glue,(enum usb_role)99)==-EINVAL && trace_n==0);
 reset(USB_ROLE_NONE,false,true);memcpy(saved,regs,sizeof(regs));on_error=-ETIMEDOUT;
 assert(mtk_otg_switch_set(&glue,USB_ROLE_DEVICE)==-ETIMEDOUT && !strcmp(trace,"P") && power_count==0);fault_unchanged(USB_ROLE_NONE,PHY_MODE_USB_OTG,saved,1);
 reset(USB_ROLE_NONE,false,true);memcpy(saved,regs,sizeof(regs));mode_errors[0]=-EIO;
 assert(mtk_otg_switch_set(&glue,USB_ROLE_DEVICE)==-EIO && !strcmp(trace,"PMMO") && power_count==0);fault_unchanged(USB_ROLE_NONE,PHY_MODE_USB_OTG,saved,1);
 reset(USB_ROLE_NONE,false,true);memcpy(saved,regs,sizeof(regs));mode_errors[0]=-EIO;mode_errors[1]=-ENODEV;off_error=-EBUSY;
 assert(mtk_otg_switch_set(&glue,USB_ROLE_DEVICE)==-EIO && !strcmp(trace,"PMMO") && power_count==1 && glue.phy_powered);fault_unchanged(USB_ROLE_NONE,PHY_MODE_USB_OTG,saved,3);
 reset(USB_ROLE_HOST,true,true);memcpy(saved,regs,sizeof(regs));off_error=-EBUSY;
 assert(mtk_otg_switch_set(&glue,USB_ROLE_NONE)==-EBUSY && !strcmp(trace,"MOM") && power_count==1);fault_unchanged(USB_ROLE_HOST,PHY_MODE_USB_HOST,saved,1);
 reset(USB_ROLE_DEVICE,true,true);memcpy(saved,regs,sizeof(regs));mode_errors[0]=-EIO;
 assert(mtk_otg_switch_set(&glue,USB_ROLE_HOST)==-EIO && !strcmp(trace,"MM") && power_count==1);fault_unchanged(USB_ROLE_DEVICE,PHY_MODE_USB_DEVICE,saved,1);
 reset(USB_ROLE_NONE,false,true);on_error=-ETIMEDOUT;assert(mtk_musb_set_mode(&musb,MUSB_PERIPHERAL)==-ETIMEDOUT && glue.role==USB_ROLE_NONE && register_writes==0);
 reset(USB_ROLE_HOST,true,true);off_error=-EBUSY;struct usb_role_switch sw={.data=&glue};assert(musb_usb_role_sx_set(&sw,USB_ROLE_NONE)==-EBUSY && glue.role==USB_ROLE_HOST && register_writes==0);
 reset(USB_ROLE_HOST,true,true);memcpy(saved,regs,sizeof(regs));off_error=-EBUSY;mode_errors[1]=-ENODEV;
 assert(mtk_otg_switch_set(&glue,USB_ROLE_NONE)==-EBUSY && !strcmp(trace,"MOM"));fault_unchanged(USB_ROLE_HOST,PHY_MODE_USB_HOST,saved,2);
 /* Every init failure returns the primary error and never enables interrupts. */
 for(int phase=0;phase<5;phase++) {
  reset(USB_ROLE_NONE,false,false);
  if(phase==0)init_error=-EIO;
  if(phase==1)on_error=-EIO;
  if(phase>=2)mode_errors[0]=-EIO;
  if(phase==3)off_error=-EBUSY;
  if(phase==4)exit_error=-ENODEV;
  assert(mtk_musb_init(&musb)==-EIO && !glue.role_ready && glue.role_faulted && irq_enables==0 && registered==1 && unregistered==1);
  if(phase<3)assert(init_count==0 && power_count==0);
  if(phase==3)assert(init_count==1 && power_count==1 && strchr(trace,'E')==NULL);
  if(phase==4)assert(init_count==1 && power_count==0);
 }
 reset(USB_ROLE_NONE,false,false);registration_error=-ENODEV;assert(mtk_musb_init(&musb)==-ENODEV && !strcmp(trace,"R") && irq_enables==0);
 reset(USB_ROLE_NONE,false,false);assert(mtk_musb_init(&musb)==0 && irq_enables==1 && power_count==1 && init_count==1 && glue.role_ready);
 assert(mtk_musb_set_mode(&musb,MUSB_PERIPHERAL)==0 && power_count==1); /* no duplicate power ref */
 assert(mtk_musb_set_mode(&musb,MUSB_OTG)==0 && power_count==0);
 assert(mtk_musb_exit(&musb)==0 && init_count==0 && unregistered==1 && clocks_disabled==1 && pm_put==1 && pm_disabled==1);
 reset(USB_ROLE_DEVICE,true,true);glue.role_switch_registered=true;off_error=-EBUSY;
 assert(mtk_musb_exit(&musb)==-EBUSY && power_count==1 && init_count==1 && clocks_disabled==0 && unregistered==1 && glue.role_faulted);
 reset(USB_ROLE_DEVICE,false,false);musb.port_mode=MUSB_PERIPHERAL;assert(mtk_musb_init(&musb)==0 && registered==0 && power_count==1);
 assert(mtk_musb_set_mode(&musb,MUSB_HOST)==-EINVAL);
 assert(mtk_musb_exit(&musb)==0 && unregistered==0 && power_count==0 && init_count==0);
 reset(USB_ROLE_DEVICE,true,true);glue.strict_role_errors=false;mode_errors[0]=-EIO;
 assert(mtk_otg_switch_set(&glue,USB_ROLE_HOST)==0 && glue.role==USB_ROLE_HOST && !glue.role_faulted); /* legacy deliberately preserved */
 puts("MT8163_ROLE_RAM_CONTROLS_PASS");return 0;
}
