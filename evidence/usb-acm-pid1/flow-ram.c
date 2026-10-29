#include <assert.h>
#include <stdio.h>
#include <string.h>
#define FT_ACM_HOST_TEST 1
#include "pid1_flow.h"
struct model {int calls,mount_calls,mount_fail,security_fail,discover_fail,emit_fail,unmount_fail,bind_fail,unbind_fail;int unmounts[4],unmount_count,unbound,deleted,security_seen,discovered;};
static int mount_cb(void *c,int i){struct model *m=c;m->calls++;m->mount_calls++;if(i==3)assert(m->security_seen&&m->discovered);return m->mount_fail==i+1?-40-i:0;}
static int unmount_cb(void *c,int i){struct model *m=c;m->calls++;m->unmounts[m->unmount_count++]=i;return m->unmount_fail==i+1?-60-i:0;}
static int security_cb(void *c){struct model *m=c;m->calls++;m->security_seen=1;assert(m->mount_calls==3);return m->security_fail?-71:0;}
static int discover_cb(void *c,char *s,unsigned long cap){struct model *m=c;m->calls++;assert(m->security_seen&&cap==64);m->discovered=1;strcpy(s,"musb-hdrc.0.auto");return m->discover_fail?-72:0;}
static int emit_cb(void *c,const char *s,unsigned long n){struct model *m=c;m->calls++;assert(n==strlen(s));return m->emit_fail?-73:0;}
static int mkdir_cb(void *c,const char *p){struct model *m=c;m->calls++;assert(p[0]=='/');return 0;}
static int write_cb(void *c,const char *p,const char *s,unsigned long n){struct model *m=c;m->calls++;assert(n&&p[0]=='/');if(!strcmp(p,FT_ACM_ROOT "/UDC")){if(s[0]=='\n'){m->unbound++;return m->unbind_fail?-81:0;}return m->bind_fail?-80:0;}return 0;}
static int link_cb(void *c,const char *p,const char *q){assert(p[0]=='/'&&q[0]=='/');((struct model *)c)->calls++;return 0;}
static int delete_cb(void *c,const char *p){struct model *m=c;m->calls++;m->deleted++;assert(p[0]=='/');return 0;}
static const struct ft_acm_ops acm={mkdir_cb,write_cb,link_cb,delete_cb,delete_cb};
static const struct ft_pid1_ops ops={mount_cb,unmount_cb,security_cb,discover_cb,emit_cb,&acm};
static struct ft_admission allowed(void){struct ft_admission a={1,1,1,1,1,1,1};return a;}
int main(void){
 for(int gate=0;gate<7;gate++)for(int bad=0;bad<3;bad++){
  struct ft_admission a=allowed();int *values[]={&a.loading,&a.independent_return,&a.retained_logs,&a.device_role,&a.security_policy,&a.immutable_namespace,&a.descriptor_assignment};*values[gate]=bad==0?0:bad==1?-1:2;
  struct model m={0};struct ft_pid1_result s={0};assert(ft_pid1_flow(&ops,&m,&a,"0xffff","0xffff",&s)==-1);assert(m.calls==0);
 }
 struct ft_admission a=allowed();
 {struct model m={0};struct ft_pid1_result s={0};assert(ft_pid1_flow(&ops,&m,&a,"","0xffff",&s)==-22&&m.calls==0);}
 for(int fail=0;fail<4;fail++){
  struct model m={0};m.mount_fail=fail+1;struct ft_pid1_result s={0};assert(ft_pid1_flow(&ops,&m,&a,"0xffff","0xffff",&s)==-40-fail);assert(s.mounts==0&&m.unmount_count==fail);for(int j=0;j<fail;j++)assert(m.unmounts[j]==fail-1-j);
 }
 for(int kind=0;kind<3;kind++){
  struct model m={0};m.security_fail=kind==0;m.discover_fail=kind==1;m.emit_fail=kind==2;struct ft_pid1_result s={0};int expected=-71-kind;
  assert(ft_pid1_flow(&ops,&m,&a,"0xffff","0xffff",&s)==expected&&s.primary==expected);assert(!s.mounts&&!s.gadget.owned);if(kind<2)assert(m.mount_calls==3&&m.unbound==0);else assert(m.unbound==1&&m.deleted==6);
 }
 for(int fail=0;fail<4;fail++){
  struct model m={0};m.unmount_fail=fail+1;struct ft_pid1_result s={0};assert(ft_pid1_flow(&ops,&m,&a,"0xffff","0xffff",&s)==-60-fail);assert(s.cleanup==-60-fail&&s.mounts==((1U<<(fail+1))-1));assert(m.unmount_count==4-fail);
 }
 {struct model m={0};m.bind_fail=m.unbind_fail=1;struct ft_pid1_result s={0};assert(ft_pid1_flow(&ops,&m,&a,"0xffff","0xffff",&s)==-80);assert(s.cleanup==-81&&m.unbound==1&&m.deleted==0&&s.mounts==15&&m.unmount_count==0);}
 {struct model m={0};m.unbind_fail=1;struct ft_pid1_result s={0};assert(ft_pid1_flow(&ops,&m,&a,"0xffff","0xffff",&s)==-81);assert(s.mounts==15&&m.unmount_count==0&&m.deleted==0);}
 {struct model m={0};struct ft_pid1_result s={0};assert(ft_pid1_flow(&ops,&m,&a,"0xffff","0xffff",&s)==0);assert(!s.mounts&&!s.gadget.owned&&m.unbound==1&&m.deleted==6&&m.unmount_count==4);}
 puts("FIRETABS_ACM_PID1_FLOW_RAM_PASS");return 0;
}
