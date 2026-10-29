/* Source-only admission and owned-mount lifecycle. Tests supply RAM callbacks. */
#ifndef FIRETABS_ACM_PID1_FLOW_H
#define FIRETABS_ACM_PID1_FLOW_H
#include "acm_setup.h"
struct ft_admission {
 int loading, independent_return, retained_logs, device_role, security_policy;
 int immutable_namespace, descriptor_assignment;
};
struct ft_pid1_ops {
 int (*mount)(void *,int);
 int (*unmount)(void *,int);
 int (*security)(void *);
 int (*discover)(void *,char *,unsigned long);
 int (*emit)(void *,const char *,unsigned long);
 const struct ft_acm_ops *acm;
};
struct ft_pid1_result { unsigned int mounts; int primary,cleanup; struct ft_acm_state gadget; };
static int ft_admitted(const struct ft_admission *a) {
 return a && a->loading==1 && a->independent_return==1 && a->retained_logs==1 &&
 a->device_role==1 && a->security_policy==1 && a->immutable_namespace==1 && a->descriptor_assignment==1;
}
static int ft_pid1_finish(const struct ft_pid1_ops *o,void *ctx,struct ft_pid1_result *s) {
 if(s->gadget.cleanup_error){s->cleanup=s->gadget.cleanup_error;return s->cleanup;}
 int r=ft_acm_cleanup(o->acm,ctx,&s->gadget);
 if(r){s->cleanup=r;return r;} /* Keep all mounts if gadget may still be active/owned. */
 for(int i=3;i>=0;i--)if(s->mounts&(1U<<i)) {
  r=o->unmount(ctx,i);if(r){s->cleanup=r;return r;}
  s->mounts&=~(1U<<i);
 }
 return 0;
}
static int ft_pid1_flow(const struct ft_pid1_ops *o,void *ctx,const struct ft_admission *a,
 const char *vid,const char *pid,struct ft_pid1_result *s) {
 if(!o||!o->mount||!o->unmount||!o->security||!o->discover||!o->emit||!o->acm||
 !o->acm->mkdir||!o->acm->write||!o->acm->link||!o->acm->unlink||!o->acm->rmdir||!s)return -22;
 if(s->mounts||s->primary||s->cleanup||s->gadget.owned||s->gadget.bind_attempted||s->gadget.bound||s->gadget.cleanup_error)return -16;
 if(!ft_admitted(a))return -1; /* No mount, discovery or gadget callback without every gate. */
 if(!ft_acm_identity(vid)||!ft_acm_identity(pid))return -22;
 int r=0;char udc[64];
 /* proc, read-only sysfs, read-only selinuxfs; configfs only after enforcing check. */
 for(int i=0;i<3;i++){r=o->mount(ctx,i);if(r)goto failed;s->mounts|=1U<<i;}
 r=o->security(ctx);if(r)goto failed;
 r=o->discover(ctx,udc,sizeof(udc));if(r)goto failed;
 r=o->mount(ctx,3);if(r)goto failed;s->mounts|=8;
 r=ft_acm_setup(o->acm,ctx,&s->gadget,udc,vid,pid,1);if(r)goto failed;
 r=o->emit(ctx,"FIRETABS_ACM_SOURCE_SETUP_COMPLETE\n",sizeof("FIRETABS_ACM_SOURCE_SETUP_COMPLETE\n")-1);
 /* One-shot source lifecycle; no claim that host received these console bytes. */
failed:
 s->primary=r;
 {int cleanup=ft_pid1_finish(o,ctx,s);return r?r:cleanup;}
}
#endif
