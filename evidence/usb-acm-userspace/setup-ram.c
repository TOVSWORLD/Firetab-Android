#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "acm_setup.h"
struct model {int calls,fail_at,cleanup_fail,unbinds;unsigned int objects;};
static const char *paths[]={FT_ACM_ROOT,FT_ACM_ROOT "/strings/0x409",FT_ACM_ROOT "/configs/c.1",FT_ACM_ROOT "/configs/c.1/strings/0x409",FT_ACM_ROOT "/functions/acm.usb0",FT_ACM_ROOT "/configs/c.1/acm.usb0"};
static int index_of(const char *p) {for(int i=0;i<6;i++)if(!strcmp(p,paths[i]))return i;return -1;}
static int step(struct model *m) {m->calls++;return m->calls==m->fail_at?-5:0;}
static int mkdir_op(void *ctx,const char *p) {struct model *m=ctx;int i=index_of(p),r=step(m);assert(i>=0&&i<5);if(!r)m->objects|=1U<<i;return r;}
static int write_op(void *ctx,const char *p,const char *s,unsigned long n) {struct model *m=ctx;assert(strncmp(p,FT_ACM_ROOT,strlen(FT_ACM_ROOT))==0);if(!strcmp(p,FT_ACM_ROOT "/UDC")&&n==1&&s[0]=='\n'){m->unbinds++;return m->cleanup_fail?-6:0;}assert(n==strlen(s));return step(m);}
static int link_op(void *ctx,const char *target,const char *path) {struct model *m=ctx;assert(!strcmp(target,paths[4])&&!strcmp(path,paths[5]));int r=step(m);if(!r)m->objects|=32;return r;}
static int remove_op(void *ctx,const char *p) {struct model *m=ctx;int i=index_of(p);assert(i>=0 &&(m->objects&(1U<<i)));if(m->cleanup_fail)return -6;m->objects&=~(1U<<i);return 0;}
int main(void) {
 struct ft_acm_ops ops={mkdir_op,write_op,link_op,remove_op,remove_op};struct ft_acm_state s={0};struct model m={0};
 assert(ft_acm_setup(&ops,&m,&s,"mock-udc","0xffff","0xffff",0)==-1&&m.calls==0);
 assert(ft_acm_setup(&ops,&m,&s,"../bad","0xffff","0xffff",1)==-22&&m.calls==0);
 assert(ft_acm_setup(&ops,&m,&s,"mock","bad","0xffff",1)==-22&&m.calls==0);
 assert(ft_acm_setup(&ops,&m,&s,"mock-udc","0xffff","0xffff",1)==0&&m.calls==12&&s.bound&&m.objects==63);
 assert(ft_acm_setup(&ops,&m,&s,"mock-udc","0xffff","0xffff",1)==-16);
 assert(ft_acm_cleanup(&ops,&m,&s)==0&&m.objects==0&&!s.bound&&!s.owned&&m.unbinds==1);
 for(int fail=1;fail<=12;fail++) {
  m=(struct model){.fail_at=fail};s=(struct ft_acm_state){0};assert(ft_acm_setup(&ops,&m,&s,"mock-udc","0xffff","0xffff",1)==-5);
  assert(!m.objects&&!s.owned&&!s.bound);if(fail==12)assert(m.unbinds==1);
 }
 m=(struct model){.fail_at=12,.cleanup_fail=1};s=(struct ft_acm_state){0};assert(ft_acm_setup(&ops,&m,&s,"mock","0xffff","0xffff",1)==-5&&s.cleanup_error==-6&&s.owned==63&&s.bind_attempted);
 m=(struct model){.fail_at=5,.cleanup_fail=1};s=(struct ft_acm_state){0};assert(ft_acm_setup(&ops,&m,&s,"mock","0xffff","0xffff",1)==-5&&s.cleanup_error==-6&&s.owned==3&&m.unbinds==0);
 char long_udc[65];memset(long_udc,'a',64);long_udc[64]=0;m=(struct model){0};s=(struct ft_acm_state){0};assert(ft_acm_setup(&ops,&m,&s,long_udc,"0xffff","0xffff",1)==-22&&m.calls==0);
 puts("FIRETABS_ACM_SETUP_RAM_CONTROLS_PASS");return 0;
}
