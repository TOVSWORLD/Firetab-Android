#include <assert.h>
#include <stdio.h>
#include <string.h>
#define FT_ACM_HOST_TEST 1
#define FT_PID1_HOST_TEST 1
#include "init.c"
struct model {int fail,mode,calls,port_opens,mknods,tty_opens,gets,sets,writes,sleeps,tty_closes,unlinks;unsigned long offsets[32],used;char output[256];struct ft_termios settings;};
static void put32(unsigned char *p,unsigned int n){for(int i=0;i<4;i++)p[i]=(unsigned char)(n>>(8*i));}
static long fake(void *c,long nr,long a,long b,long d,long e,long f,long g){
 struct model *m=c;m->calls++;(void)g;
 if(nr==FT_NR_OPENAT){const char *p=(const char *)b;assert(a==FT_AT_FDCWD&&(d&FT_O_NOFOLLOW)&&(d&FT_O_CLOEXEC));
  if(!strcmp(p,FT_SERIAL_PORT_PATH)){m->port_opens++;m->offsets[10]=0;return 10;}
  if(!strcmp(p,"/sys/class/tty/ttyGS2/dev")){m->offsets[11]=0;return 11;}
  assert(!strcmp(p,FT_SERIAL_NODE));assert((d&(FT_O_WRONLY|FT_SERIAL_NOCTTY|FT_SERIAL_NONBLOCK))==(FT_O_WRONLY|FT_SERIAL_NOCTTY|FT_SERIAL_NONBLOCK));m->tty_opens++;return m->fail==4?-13:20;
 }
 if(nr==FT_NR_READ){assert(a==10||a==11);const char *s=a==10?"2\n":"273:1025\n";
  if(m->fail==1&&a==10)s="02\n";
  if(m->fail==2&&a==11)s="273:1048576\n";
  if(m->fail==9&&a==10&&m->port_opens==2)s="1\n";
  unsigned long n=strlen(s)-m->offsets[a];
  if(n>(unsigned long)d)n=(unsigned long)d;
  memcpy((void *)b,s+m->offsets[a],n);m->offsets[a]+=n;return (long)n;
 }
 if(nr==FT_SERIAL_MKNODAT){assert(a==FT_AT_FDCWD&&!strcmp((char *)b,FT_SERIAL_NODE)&&d==(FT_SERIAL_IFCHR|0600));
  unsigned int encoded=(unsigned int)e;assert(((encoded&0xfff00)>>8)==273);assert(((encoded&0xff)|((encoded>>12)&0xfff00))==1025);m->mknods++;return m->fail==3?-17:0;
 }
 if(nr==FT_SERIAL_STATX){assert(a==20&&!*(char *)b&&d==FT_SERIAL_AT_EMPTY_PATH&&e==FT_SERIAL_STATX_TYPE);
  if(m->fail==5)return -38;
  unsigned char *st=(unsigned char *)f;memset(st,0,256);put32(st,m->fail==6?0:1);st[28]=0;st[29]=m->fail==7?0x80:0x20;put32(st+128,m->fail==8?274:273);put32(st+132,1025);return 0;
 }
 if(nr==FT_SERIAL_IOCTL){assert(a==20);struct ft_termios *t=(struct ft_termios *)d;
  if(b==FT_SERIAL_TCGETS){m->gets++;
  if((m->mode==6&&m->gets<=2)||m->mode==7)return -4;
  if(m->fail==10&&m->gets==1)return -25;
  if(m->fail==13&&m->gets==2)return -5;
  *t=m->settings;
  if(m->fail==11&&m->gets==1)t->line=1;
  if(m->fail==14&&m->gets==2)t->oflag=1;
  return 0;}
  assert(b==FT_SERIAL_TCSETS);m->sets++;
  if((m->fail==12&&m->sets==1)||(m->fail==20&&m->sets==2))return -5;
  if(m->sets==1){assert(t->iflag==0&&t->oflag==0&&t->lflag==0&&t->line==0);assert(t->cflag==(FT_SERIAL_B9600|FT_SERIAL_CS8|FT_SERIAL_CREAD|FT_SERIAL_CLOCAL));assert(t->cc[FT_SERIAL_VMIN]==1&&t->cc[FT_SERIAL_VTIME]==0);}
  m->settings=*t;return 0;
 }
 if(nr==FT_NR_WRITE){assert(a==20);m->writes++;assert((unsigned long)d==sizeof(ft_serial_frame)-1-m->used);assert(!memcmp((void *)b,ft_serial_frame+m->used,(unsigned long)d));
  if(m->fail==15)return -5;
  if(m->fail==16)return 0;
  if(m->fail==17)return d+1;
  if(m->fail==18||m->fail==23)return -11;
  if(m->fail==19)return -4;
  if(m->mode==1&&m->writes<3)return -4;
  if(m->mode==2&&m->writes<3)return -11;
  unsigned long n=m->mode==3?1:m->mode==4&&d>4?4:(unsigned long)d;memcpy(m->output+m->used,(void *)b,n);m->used+=n;return (long)n;
 }
 if(nr==FT_SERIAL_NANOSLEEP){const long *delay=(long *)a;assert(delay[0]==0&&delay[1]==10000000&&b==0);m->sleeps++;return m->fail==23?-22:0;}
 if(nr==FT_NR_CLOSE){if(a==20){m->tty_closes++;return m->fail==21?-4:0;}assert(a==10||a==11);return 0;}
 if(nr==FT_NR_UNLINKAT){assert(a==FT_AT_FDCWD&&!strcmp((char *)b,FT_SERIAL_NODE)&&d==0);m->unlinks++;return m->fail==22||m->mode==5?-13:0;}
 assert(0);return -99;
}
static struct ft_termios original(void){struct ft_termios t={0x501,5,0x4bd,0x8a3b,0,{0}};t.cc[0]=3;return t;}
static struct ft_serial_state empty_state(void){struct ft_serial_state s={-1,0,0,0,0,0,{0}};return s;}
int main(void){
 unsigned int p,ma,mi;char path[32];
 assert(ft_acm_setup(0,0,0,0,0,0,0)==-22);assert(ft_discover_udc(0,path,sizeof(path))==-22);
 const char *badports[]={"","-1\n","256\n","2","2\n\n","02\n","2 \n","9999999999999999999999\n"};
 for(unsigned int i=0;i<sizeof(badports)/sizeof(badports[0]);i++)assert(ft_serial_port(badports[i],strlen(badports[i]),&p)==-22);
 const char *baddevs[]={"0:1\n","4096:1\n","1:1048576\n","1:-1\n","1:01\n","1:1","1:1\nextra","1::1\n"};
 for(unsigned int i=0;i<sizeof(baddevs)/sizeof(baddevs[0]);i++)assert(ft_serial_device(baddevs[i],strlen(baddevs[i]),&ma,&mi)==-22);
 assert(!ft_serial_port("0\n",2,&p)&&p==0);assert(!ft_serial_port("255\n",4,&p)&&p==255);assert(!ft_serial_devpath(path,255)&&!strcmp(path,"/sys/class/tty/ttyGS255/dev"));assert(ft_serial_devpath(path,256)==-22);
 assert(!ft_serial_device("4095:1048575\n",13,&ma,&mi)&&ma==4095&&mi==1048575);
 for(int mode=0;mode<5;mode++){struct model m={0};m.settings=original();m.mode=mode;struct ft_acm_io io={fake,&m};struct ft_serial_state s=empty_state();
  assert(ft_serial_output(&io,1,1,&s)==0);assert(s.accepted==sizeof(ft_serial_frame)-1&&m.used==s.accepted&&!memcmp(m.output,ft_serial_frame,m.used));assert(m.tty_closes==1&&m.unlinks==1&&m.sets==2&&!s.node_owned&&!s.restore_needed);struct ft_termios t=original();assert(!memcmp(&m.settings,&t,sizeof(t)));assert(m.writes<=128);
 }
 {struct model m={0};m.settings=original();m.mode=6;struct ft_acm_io io={fake,&m};struct ft_serial_state s=empty_state();assert(ft_serial_output(&io,1,1,&s)==0&&m.gets==4);}
 {struct model m={0};m.settings=original();m.mode=7;struct ft_acm_io io={fake,&m};struct ft_serial_state s=empty_state();assert(ft_serial_output(&io,1,1,&s)==-4&&m.gets==8&&m.sets==0&&m.tty_closes==1);}
 for(int fail=1;fail<=23;fail++){struct model m={0};m.settings=original();m.fail=fail;struct ft_acm_io io={fake,&m};struct ft_serial_state s=empty_state();int r=ft_serial_output(&io,1,1,&s);assert(r<0);assert(m.writes<=128&&m.sleeps<=128&&m.tty_closes<=1);
  if(fail<=3)assert(m.unlinks==0&&m.tty_closes==0);else assert(m.unlinks==1);
  if(fail>=5&&fail<=11)assert(m.sets==0&&m.writes==0);
  if(fail==18||fail==19)assert(r==-110&&m.writes==128);
  if(fail==20)assert(s.cleanup==-5&&s.restore_needed&&m.tty_closes==1);
  if(fail==21)assert(s.cleanup==-4&&m.tty_closes==1);
  if(fail==22)assert(s.cleanup==-13&&s.node_owned);
 }
 {struct model m={0};struct ft_acm_io io={fake,&m};struct ft_serial_state s=empty_state();assert(ft_serial_output(&io,0,1,&s)==-1&&m.calls==0);assert(ft_serial_output(&io,1,0,&s)==-1&&m.calls==0);s.node_owned=1;assert(ft_serial_output(&io,1,1,&s)==-16&&m.calls==0);}
 {struct model m={0};m.settings=original();m.fail=15;m.mode=5;struct ft_acm_io io={fake,&m};struct ft_serial_state s=empty_state();assert(ft_serial_output(&io,1,1,&s)==-5&&s.primary==-5&&s.cleanup==-13&&s.node_owned);}
 {struct model m={0};m.settings=original();struct ft_acm_io io={fake,&m};
  const char marker[]="FIRETABS_ACM_SOURCE_SETUP_COMPLETE\n";
  assert(emit_acm(&io,"bad",3)==-22&&m.calls==0);assert(emit_acm(&io,marker,sizeof(marker)-1)==0&&m.used==sizeof(ft_serial_frame)-1);
  struct ft_pid1_ops ops={mount_virtual,unmount_virtual,security_enforcing,discover,emit_acm,&ft_acm_filesystem_ops};
  struct ft_admission deny={0};struct ft_pid1_result state={0};int calls=m.calls;
  assert(ft_pid1_flow(&ops,&io,&deny,"","",&state)==-1&&m.calls==calls);console=-1;assert(emit_console(&io,"x",1)==-19&&m.calls==calls);
 }
 puts("FIRETABS_ACM_SERIAL_RAM_PASS");return 0;
}
