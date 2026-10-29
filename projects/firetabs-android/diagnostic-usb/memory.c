/* Freestanding compiler support; volatile stores prevent recursive builtin folding. */
void *memset(void *dest,int value,unsigned long count) {
 volatile unsigned char *out=dest;
 for(unsigned long i=0;i<count;i++)out[i]=(unsigned char)value;
 return dest;
}
void *memcpy(void *dest,const void *src,unsigned long count) {
 volatile unsigned char *out=dest;const volatile unsigned char *in=src;
 for(unsigned long i=0;i<count;i++)out[i]=in[i];
 return dest;
}
