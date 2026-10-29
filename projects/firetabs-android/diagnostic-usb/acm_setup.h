/* Isolated callback transaction; no implicit runtime or device admission. */
#ifndef FIRETABS_ACM_SETUP_H
#define FIRETABS_ACM_SETUP_H
#define FT_ACM_ROOT "/config/usb_gadget/firetabs-diagnostic"
struct ft_acm_ops {
 int (*mkdir)(void *,const char *);
 int (*write)(void *,const char *,const char *,unsigned long);
 int (*link)(void *,const char *,const char *);
 int (*unlink)(void *,const char *);
 int (*rmdir)(void *,const char *);
};
struct ft_acm_state { unsigned int owned;int bind_attempted,bound,cleanup_error; };
static unsigned long ft_acm_length(const char *s) {unsigned long n=0;while(n<64&&s[n])n++;return n;}
static int ft_acm_identity(const char *s) {
 if(!s ||ft_acm_length(s)!=6 ||s[0]!='0'||s[1]!='x')return 0;
 for(int i=2;i<6;i++)if(!((s[i]>='0'&&s[i]<='9')||(s[i]>='a'&&s[i]<='f')||(s[i]>='A'&&s[i]<='F')))return 0;
 return 1; /* syntax only; no production VID/PID assignment claim */
}
static int ft_acm_udc(const char *s) {
 unsigned long n;
 if(!s)return 0;
 n=ft_acm_length(s);
 if(!n||n>63)return 0;
 if((n==1&&s[0]=='.')||(n==2&&s[0]=='.'&&s[1]=='.'))return 0;
 for(unsigned long i=0;i<n;i++)if(!((s[i]>='A'&&s[i]<='Z')||(s[i]>='a'&&s[i]<='z')||(s[i]>='0'&&s[i]<='9')||s[i]=='.'||s[i]=='_'||s[i]=='-'))return 0;
 return 1;
}
static int ft_acm_cleanup(const struct ft_acm_ops *o,void *ctx,struct ft_acm_state *s) {
 int ret;
 if(s->bind_attempted) {
  ret=o->write(ctx,FT_ACM_ROOT "/UDC","\n",1);
  if(ret){s->cleanup_error=ret;return ret;}
  s->bind_attempted=s->bound=0;
 }
 static const char * const paths[]={FT_ACM_ROOT,FT_ACM_ROOT "/strings/0x409",FT_ACM_ROOT "/configs/c.1",FT_ACM_ROOT "/configs/c.1/strings/0x409",FT_ACM_ROOT "/functions/acm.usb0",FT_ACM_ROOT "/configs/c.1/acm.usb0"};
 for(int i=5;i>=0;i--)if(s->owned&(1U<<i)) {
  ret=i==5?o->unlink(ctx,paths[i]):o->rmdir(ctx,paths[i]);
  if(ret){s->cleanup_error=ret;return ret;}
  s->owned&=~(1U<<i);
 }
 return 0;
}
static int ft_acm_setup(const struct ft_acm_ops *o,void *ctx,struct ft_acm_state *s,const char *udc,const char *vid,const char *pid,int admitted) {
 int ret;
 if(!o||!o->mkdir||!o->write||!o->link||!o->unlink||!o->rmdir||!s||!ft_acm_udc(udc)||!ft_acm_identity(vid)||!ft_acm_identity(pid))return -22;
 if(!admitted)return -1; /* external loading/device-role gate; false in current prototypes */
 if(s->owned||s->bind_attempted||s->bound||s->cleanup_error)return -16;
 static const char * const dirs[]={FT_ACM_ROOT,FT_ACM_ROOT "/strings/0x409",FT_ACM_ROOT "/configs/c.1",FT_ACM_ROOT "/configs/c.1/strings/0x409",FT_ACM_ROOT "/functions/acm.usb0"};
 ret=o->mkdir(ctx,dirs[0]);if(ret)return ret;s->owned|=1;
 ret=o->write(ctx,FT_ACM_ROOT "/idVendor",vid,6);if(ret)goto fail;
 ret=o->write(ctx,FT_ACM_ROOT "/idProduct",pid,6);if(ret)goto fail;
 ret=o->mkdir(ctx,dirs[1]);if(ret)goto fail;s->owned|=2;
 ret=o->write(ctx,FT_ACM_ROOT "/strings/0x409/manufacturer","FireTabs laboratory",19);if(ret)goto fail;
 ret=o->write(ctx,FT_ACM_ROOT "/strings/0x409/product","Diagnostic ACM",14);if(ret)goto fail;
 ret=o->mkdir(ctx,dirs[2]);if(ret)goto fail;s->owned|=4;
 ret=o->mkdir(ctx,dirs[3]);if(ret)goto fail;s->owned|=8;
 ret=o->write(ctx,FT_ACM_ROOT "/configs/c.1/strings/0x409/configuration","Diagnostic ACM",14);if(ret)goto fail;
 ret=o->mkdir(ctx,dirs[4]);if(ret)goto fail;s->owned|=16;
 ret=o->link(ctx,dirs[4],FT_ACM_ROOT "/configs/c.1/acm.usb0");if(ret)goto fail;s->owned|=32;
 s->bind_attempted=1;
 ret=o->write(ctx,FT_ACM_ROOT "/UDC",udc,ft_acm_length(udc));if(ret)goto fail;
 s->bound=1;return 0;
fail:
 ft_acm_cleanup(o,ctx,s);return ret;
}
#endif
