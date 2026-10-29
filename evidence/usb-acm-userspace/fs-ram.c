#include <assert.h>
#include <stdio.h>
#include <string.h>
#define FT_ACM_HOST_TEST 1
#include "acm_fs.h"
#include <stddef.h>
typedef unsigned long long u64;typedef signed long long s64;
#include "source/dirent.h"
_Static_assert(offsetof(struct linux_dirent64,d_reclen)==16,"reclen ABI");
_Static_assert(offsetof(struct linux_dirent64,d_type)==18,"type ABI");
_Static_assert(offsetof(struct linux_dirent64,d_name)==19,"name ABI");
struct model {
 int calls,writes,closes,eintr,short_write,zero_write,write_error,close_error,empty_udc;
 int entries,dir_done,bad_record,bad_controller,bad_compat,otg,dir_close_error,never_end,long_name;
 unsigned long read_pos;int read_kind;
};
static const char compatible[]="mediatek,mt8163-musb\0mediatek,mtk-musb";
static unsigned long dirent(unsigned char *b,const char *name) {
 unsigned long len=strlen(name),n=(19+len+1+7)&~7UL;memset(b,0,n);b[16]=(unsigned char)n;b[17]=(unsigned char)(n>>8);b[18]=10;memcpy(b+19,name,len);return n;
}
static long fake(void *ctx,long nr,long a,long b,long c,long d,long e,long f) {
 struct model *m=ctx;m->calls++;(void)d;(void)e;(void)f;
 if(nr==FT_NR_OPENAT) {
  const char *path=(const char *)b;assert(a==FT_AT_FDCWD&&(c&FT_O_CLOEXEC)&&(c&FT_O_NOFOLLOW));
  if(ft_same(path,"/sys/class/udc")){assert(c&FT_O_DIRECTORY);return 10;}
  if(c&FT_O_WRONLY){assert(ft_write_path(path));return 20;}
  m->read_pos=0;
  if(ft_same(path,FT_ACM_ROOT "/UDC"))m->read_kind=4;
  else if(strstr(path,"/device/of_node/compatible"))m->read_kind=1;
  else if(strstr(path,"/device/of_node/reg"))m->read_kind=2;
  else {assert(strstr(path,"/device/of_node/dr_mode"));m->read_kind=3;}
  return 21;
 }
 if(nr==FT_NR_CLOSE){m->closes++;return a==10?m->dir_close_error:m->close_error;}
 if(nr==FT_NR_WRITE) {
  assert(a==20);m->writes++;
  if(m->eintr){m->eintr--;return -4;}
  if(m->write_error)return m->write_error;
  if(m->zero_write)return 0;
  if(m->short_write)return c-1;
  assert((unsigned long)c==strlen((const char *)b));return c;
 }
 if(nr==FT_NR_READ) {
  assert(a==21);const char *data;unsigned long len;
  unsigned char reg[]={0,0,0,0,0x11,0x20,0,0,0,0,0,0,0,0,0x10,0};
  if(m->bad_controller)reg[5]=0x27;
  if(m->read_kind==1){data=m->bad_compat?"bad":compatible;len=m->bad_compat?4:sizeof(compatible);}
  else if(m->read_kind==2){data=(const char *)reg;len=sizeof(reg);}
  else if(m->read_kind==3){data=m->otg?"otg":"peripheral";len=m->otg?sizeof("otg"):sizeof("peripheral");}
  else {data=m->empty_udc?"\n":"still-bound\n";len=strlen(data);}
  unsigned long n=m->read_pos>=len?0:len-m->read_pos;if(n>(unsigned long)c)n=(unsigned long)c;
  memcpy((void *)b,data+m->read_pos,n);m->read_pos+=n;return (long)n;
 }
 if(nr==FT_NR_GETDENTS64) {
  assert(a==10&&c==2048);if(m->dir_done++&&!m->never_end)return 0;
  unsigned char *buf=(unsigned char *)b;unsigned long n=dirent(buf,".");n+=dirent(buf+n,"..");
  if(m->entries) {char long_name[65];memset(long_name,'a',64);long_name[64]=0;n+=dirent(buf+n,m->long_name?long_name:"mock-udc");}
  if(m->entries>1)n+=dirent(buf+n,"other-udc");
  if(m->bad_record==1)buf[16]=0;
  if(m->bad_record==2)buf[16]=23;
  if(m->bad_record==3)buf[16]=248;
  if(m->bad_record==4)memset(buf+19,'a',5);
  if(m->bad_record==5)n=19;
  return (long)n;
 }
 if(nr==FT_NR_MKDIRAT){assert(a==FT_AT_FDCWD&&ft_resource((const char *)b)>=0&&c==0700);return 0;}
 if(nr==FT_NR_SYMLINKAT){assert(ft_resource((const char *)a)==4&&b==FT_AT_FDCWD&&ft_resource((const char *)c)==5);return 0;}
 if(nr==FT_NR_UNLINKAT){assert(a==FT_AT_FDCWD&&ft_resource((const char *)b)>=0&&(c==0||c==FT_AT_REMOVEDIR));return 0;}
 assert(!"unexpected syscall");return -22;
}
int main(void) {
 struct model m={0};struct ft_acm_io io={fake,&m};
 assert(ft_fs_write(&io,FT_ACM_ROOT "/idVendor","0xffff",6)==0&&m.writes==1&&m.closes==1);
 m=(struct model){.short_write=1};assert(ft_fs_write(&io,FT_ACM_ROOT "/idVendor","0xffff",6)==-5&&m.writes==1&&m.closes==1);
 m=(struct model){.zero_write=1};assert(ft_fs_write(&io,FT_ACM_ROOT "/idVendor","0xffff",6)==-5&&m.writes==1);
 m=(struct model){.eintr=2};assert(ft_fs_write(&io,FT_ACM_ROOT "/idVendor","0xffff",6)==0&&m.writes==3);
 m=(struct model){.eintr=20};assert(ft_fs_write(&io,FT_ACM_ROOT "/idVendor","0xffff",6)==-4&&m.writes==8&&m.closes==1);
 m=(struct model){.close_error=-4};assert(ft_fs_write(&io,FT_ACM_ROOT "/idVendor","0xffff",6)==-4&&m.closes==1);
 m=(struct model){.write_error=-19,.empty_udc=1};assert(ft_fs_write(&io,FT_ACM_ROOT "/UDC","\n",1)==0&&m.writes==1&&m.closes==2);
 m=(struct model){.write_error=-19};assert(ft_fs_write(&io,FT_ACM_ROOT "/UDC","\n",1)==-19&&m.closes==2);
 m=(struct model){0};assert(ft_fs_write(&io,"/tmp/not-owned","x",1)==-22&&m.calls==0);
 assert(ft_fs_mkdir(&io,"/tmp/not-owned")==-22&&m.calls==0);
 assert(ft_fs_unlink(&io,FT_ACM_ROOT)==-22&&m.calls==0);
 assert(ft_fs_rmdir(&io,FT_ACM_ROOT "/configs/c.1/acm.usb0")==-22&&m.calls==0);
 char name[64];m=(struct model){.entries=1};assert(ft_discover_udc(&io,name,sizeof(name))==0&&!strcmp(name,"mock-udc")&&m.writes==0);
 for(int test=0;test<6;test++) {
  m=(struct model){.entries=1};memset(name,'x',sizeof(name));
  if(test==0)m.entries=0;
  if(test==1)m.entries=2;
  if(test==2)m.bad_record=1;
  if(test==3)m.bad_controller=1;
  if(test==4)m.bad_compat=1;
  if(test==5)m.otg=1;
  assert(ft_discover_udc(&io,name,sizeof(name))<0&&m.writes==0&&name[0]=='x');
 }
 m=(struct model){.entries=1,.dir_close_error=-5};assert(ft_discover_udc(&io,name,sizeof(name))==-5&&m.writes==0);
 for(int bad=1;bad<=5;bad++) {m=(struct model){.entries=1,.bad_record=bad};assert(ft_discover_udc(&io,name,sizeof(name))<0&&m.writes==0);}
 m=(struct model){.entries=1,.long_name=1};assert(ft_discover_udc(&io,name,sizeof(name))==-22&&m.writes==0);
 m=(struct model){.entries=0,.never_end=1};assert(ft_discover_udc(&io,name,sizeof(name))==-75&&m.writes==0);
 m=(struct model){0};char tiny[1];assert(ft_read_file(&io,FT_ACM_ROOT "/UDC",tiny,sizeof(tiny))==-75&&m.closes==1);
 m=(struct model){0};struct ft_acm_state state={0};
 assert(ft_acm_setup(&ft_acm_filesystem_ops,&io,&state,"mock-udc","0xffff","0xffff",0)==-1&&m.calls==0);
 assert(ft_acm_setup(&ft_acm_filesystem_ops,&io,&state,"mock-udc","0xffff","0xffff",1)==0&&state.bound);
 assert(ft_acm_cleanup(&ft_acm_filesystem_ops,&io,&state)==0&&!state.owned&&!state.bound);
 puts("FIRETABS_ACM_FS_RAM_CONTROLS_PASS");return 0;
}
