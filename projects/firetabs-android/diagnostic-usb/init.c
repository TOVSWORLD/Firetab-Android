/* Separate opt-in AArch64 static PID1. Current package always denies gadget setup. */
#include "acm_fs.h"
#include "pid1_flow.h"
#include "admission.h"
#define FT_NR_MOUNT 40
#define FT_NR_UMOUNT2 39
#define FT_NR_NANOSLEEP 101
#define FT_O_NONBLOCK 00004000
#ifndef FT_PID1_HOST_TEST
static long raw_call(void *ctx,long nr,long a,long b,long c,long d,long e,long f) {
 (void)ctx;
 register long x0 __asm__("x0")=a;register long x1 __asm__("x1")=b;
 register long x2 __asm__("x2")=c;register long x3 __asm__("x3")=d;
 register long x4 __asm__("x4")=e;register long x5 __asm__("x5")=f;
 register long x8 __asm__("x8")=nr;
 __asm__ volatile("svc #0":"+r"(x0):"r"(x1),"r"(x2),"r"(x3),"r"(x4),"r"(x5),"r"(x8):"memory","cc");
 return x0;
}
#endif
static const char * const targets[]={"/proc","/sys","/security","/config"};
static const char * const filesystems[]={"proc","sysfs","selinuxfs","configfs"};
static int mount_virtual(void *ctx,int i) {
 struct ft_acm_io *io=ctx;if(i<0||i>3)return -22;
 return (int)ft_call(io,FT_NR_MOUNT,(long)filesystems[i],(long)targets[i],(long)filesystems[i],i==3?14:15,0,0);
}
static int unmount_virtual(void *ctx,int i) {
 struct ft_acm_io *io=ctx;if(i<0||i>3)return -22;
 return (int)ft_call(io,FT_NR_UMOUNT2,(long)targets[i],0,0,0,0,0);
}
static int security_enforcing(void *ctx) {
 char buf[2];long n=ft_read_file(ctx,"/security/enforce",buf,sizeof(buf));
 return n==1&&buf[0]=='1'?0:-1; /* Necessary, not sufficient: policy gate remains separate. */
}
static int discover(void *ctx,char *out,unsigned long cap){return ft_discover_udc(ctx,out,cap);}
static long console=-1;
static int emit_console(void *ctx,const char *data,unsigned long n) {
 struct ft_acm_io *io=ctx;unsigned long sent=0;
 if(console<0)return -19;
 if(!n||n>128)return -22;
 for(int attempts=0;attempts<16&&sent<n;attempts++) {
  long r=ft_call(io,FT_NR_WRITE,console,(long)(data+sent),n-sent,0,0,0);
  if(r==-4)continue;
  if(r<=0)return r<0?(int)r:-5;
  if((unsigned long)r>n-sent)return -5;
  sent+=(unsigned long)r;
 }
 return sent==n?0:-5;
}
#ifndef FT_PID1_HOST_TEST
__attribute__((noreturn)) void _start(void) {
 struct ft_acm_io io={raw_call,0};
 struct ft_pid1_ops ops={mount_virtual,unmount_virtual,security_enforcing,discover,emit_console,&ft_acm_filesystem_ops};
 const struct ft_admission admission={FT_LOADING_QUALIFIED,FT_RETURN_QUALIFIED,FT_LOG_RETENTION_QUALIFIED,
 FT_DEVICE_ROLE_QUALIFIED,FT_SECURITY_POLICY_QUALIFIED,FT_IMMUTABLE_NAMESPACE_QUALIFIED,FT_DESCRIPTOR_ASSIGNMENT_QUALIFIED};
 struct ft_pid1_result result={0,0,0,{0,0,0,0}};
 long fd=ft_retry(&io,FT_NR_OPENAT,FT_AT_FDCWD,(long)"/dev/console",FT_O_WRONLY|FT_O_NONBLOCK|FT_O_NOFOLLOW|FT_O_CLOEXEC);
 if(fd>=0)console=fd; /* O_NONBLOCK: bounded attempts cannot block on console backpressure. */
 int r=ft_pid1_flow(&ops,&io,&admission,FT_PHYSICAL_VID,FT_PHYSICAL_PID,&result);
 if(r)emit_console(&io,"FIRETABS_ACM_ADMISSION_DENIED\n",sizeof("FIRETABS_ACM_ADMISSION_DENIED\n")-1);
 else emit_console(&io,"FIRETABS_ACM_SOURCE_LIFECYCLE_DONE\n",sizeof("FIRETABS_ACM_SOURCE_LIFECYCLE_DONE\n")-1);
 if(fd>=0)ft_call(&io,FT_NR_CLOSE,fd,0,0,0,0,0);
 for(;;){const long delay[2]={60,0};ft_call(&io,FT_NR_NANOSLEEP,(long)delay,0,0,0,0,0);}
}

#endif
