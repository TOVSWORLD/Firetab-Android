#include <assert.h>
#include <stdio.h>
#include <string.h>
#define FT_ACM_HOST_TEST 1
#define FT_PID1_HOST_TEST 1
#include "init.c"
#define memset ft_test_memset
#define memcpy ft_test_memcpy
#include "memory.c"
#undef memset
#undef memcpy
struct model {int calls,mounts,unmounts,mode,reads,writes,closes;long write_ret;};
static long fake(void *c,long nr,long a,long b,long d,long e,long f,long g){
 struct model *m=c;m->calls++;(void)f;(void)g;
 if(nr==FT_NR_MOUNT){assert(a==d);assert(!strcmp((char *)a,filesystems[m->mounts]));assert(!strcmp((char *)b,targets[m->mounts]));assert(e==(m->mounts==3?14:15));m->mounts++;return m->mode?-5:0;}
 if(nr==FT_NR_UMOUNT2){assert(!strcmp((char *)a,targets[m->unmounts]));assert(b==0);m->unmounts++;return m->mode?-6:0;}
 if(nr==FT_NR_OPENAT){assert(a==FT_AT_FDCWD);if(!strcmp((char *)b,"/sys/class/udc"))return -19;assert(!strcmp((char *)b,"/security/enforce"));return 12;}
 if(nr==FT_NR_READ){assert(a==12);if(m->mode==3)return -13;if(m->reads++)return 0;((char *)b)[0]=m->mode==1?'0':'1';if(m->mode==2){assert(d>=2);((char *)b)[1]='\n';return 2;}return 1;}
 if(nr==FT_NR_WRITE){assert(a==console&&d>0&&d<=128);m->writes++;if(m->mode==4&&m->writes<3)return -4;if(m->mode==5)return -4;if(m->mode==6)return 0;if(m->mode==7)return d+1;if(m->mode==8)return -5;if(m->mode==9)return 1;return d;}
 if(nr==FT_NR_CLOSE){m->closes++;return m->mode==10?-4:0;}
 assert(0);return -99;
}
int main(void){
 struct model m={0};struct ft_acm_io io={fake,&m};
 for(int i=0;i<4;i++)assert(!mount_virtual(&io,i));
 for(int i=0;i<4;i++)assert(!unmount_virtual(&io,i));
 int calls=m.calls;assert(mount_virtual(&io,-1)==-22&&unmount_virtual(&io,4)==-22&&m.calls==calls);
 for(int kind=0;kind<4;kind++){m=(struct model){0};m.mode=kind;assert(security_enforcing(&io)==(kind? -1:0));assert(m.closes==1);}
 m=(struct model){0};m.mode=10;assert(security_enforcing(&io)==-1&&m.closes==1);
 char udc[64];m=(struct model){0};assert(discover(&io,udc,64)==-19);
 console=-1;m=(struct model){0};assert(emit_console(&io,"abc",3)==-19&&m.calls==0);
 console=42;
 for(int kind=0;kind<10;kind++){m=(struct model){0};m.mode=kind;int r=emit_console(&io,"abc",3);assert((kind==5||kind==6||kind==7||kind==8)?r==-5:r==0);assert(m.writes<=16);}
 m=(struct model){0};assert(emit_console(&io,"",0)==-22&&emit_console(&io,"abc",129)==-22&&m.calls==0);
 unsigned char buf[66],src[64];for(int i=0;i<64;i++)src[i]=(unsigned char)i;
 for(unsigned long n=0;n<=64;n++){memset(buf,0xa5,sizeof(buf));assert(ft_test_memset(buf+1,0x6c,n)==buf+1);assert(buf[0]==0xa5&&buf[n+1]==0xa5);for(unsigned long i=1;i<=n;i++)assert(buf[i]==0x6c);assert(ft_test_memcpy(buf+1,src,n)==buf+1);assert(!memcmp(buf+1,src,n)&&buf[0]==0xa5&&buf[n+1]==0xa5);}
 const struct ft_pid1_ops ops={mount_virtual,unmount_virtual,security_enforcing,discover,emit_console,&ft_acm_filesystem_ops};
 struct ft_pid1_result state={0};struct ft_admission deny={0};m=(struct model){0};assert(ft_pid1_flow(&ops,&io,&deny,"","",&state)==-1&&m.calls==0);
 assert(!FT_LOADING_QUALIFIED&&!FT_SECURITY_POLICY_QUALIFIED&&!FT_DESCRIPTOR_ASSIGNMENT_QUALIFIED);
 puts("FIRETABS_ACM_PID1_ADAPTER_RAM_PASS");return 0;
}
