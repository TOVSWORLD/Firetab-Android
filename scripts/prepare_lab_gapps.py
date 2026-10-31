"""Prepare the hash-pinned ARM11 lab installer; app payloads remain unchanged.

The output is locally modified and unsigned, never a publisher-signed release.
Only for the owner-approved issue347 lab installation. No device operations.
"""
import hashlib,json,zipfile,sys,subprocess,pathlib,os,copy
SRC_SHA='cd54071df4ccd43e1c290b57508a003d253a20f23e59bba1f3d90c5fc6ad1dd0'
GUARD='''# Lab compatibility: helper executability and installed Android ABI are distinct.
GAPPS_ARCH=$(getprop2 $TMP/build.prop arch)
chmod +x "$TMP/toybox" || error "Cannot prepare package helper"
"$TMP/toybox" true || error "Package helper cannot execute in recovery"
'''
TARGET='''# Match payload ABI to installed Android userspace, never to kernel uname.
case "$(getprop2 "$SYSTEM_OUT/build.prop" ro.product.cpu.abi)" in
  armeabi-v7a|armeabi) SYSTEM_ARCH=armv7l ;;
  arm64-v8a) SYSTEM_ARCH=aarch64 ;;
  x86) SYSTEM_ARCH=i686 ;;
  x86_64) SYSTEM_ARCH=x86_64 ;;
  *) error "Unknown installed Android ABI; refusing installation" ;;
esac
[ "$GAPPS_ARCH" = "$SYSTEM_ARCH" ] || error "Package and installed Android ABI differ"
'''
def prepare(src,dst):
 assert hashlib.sha256(src.read_bytes()).hexdigest()==SRC_SHA
 z=zipfile.ZipFile(src);name='META-INF/com/google/android/update-binary';original=z.read(name).decode();assert hashlib.sha256(original.encode()).hexdigest()=='26fb0f201a625cac4c6acd25686ec6eb72a90cc032524e839e8aa5db9219cd38'
 start=original.index('# Check for arch.');end=original.index('ui_print "Setting up environment"',start)
 modified=original[:start]+GUARD+'\n'+original[end:];anchor='# Compare sdk version';assert modified.count(anchor)==1;modified=modified.replace(anchor,TARGET+'\n'+anchor)
 removed={'META-INF/MANIFEST.MF','META-INF/CERT.SF','META-INF/CERT.RSA','META-INF/com/android/otacert'}
 assert not dst.exists()
 with zipfile.ZipFile(dst,'x',compression=zipfile.ZIP_DEFLATED) as out:
  for info in z.infolist():
   if info.filename in removed:continue
   out.writestr(copy.copy(info),modified.encode() if info.filename==name else z.read(info.filename))
 with zipfile.ZipFile(dst) as out:
  same=[i.filename for i in z.infolist() if i.filename not in removed|{name}];assert all(z.read(n)==out.read(n) for n in same)
 return {'original_sha256':SRC_SHA,'modified_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'modified_bytes':dst.stat().st_size,'installer_sha256':hashlib.sha256(modified.encode()).hexdigest(),'unchanged_payload_members':len(same),'removed_stale_signature_members':sorted(removed),'publisher_signature_claim':False,'sdk_guard_preserved':'# Compare sdk version\nGAPPS_VERSION=' in modified}
def tests():
 # Execute exact target guard, retaining its fail-closed shell error behavior.
 n=0
 for abi in ['armeabi-v7a','armeabi','arm64-v8a','x86','x86_64','','unknown']:
  for package in ['armv7l','aarch64','i686','x86_64','unknown']:
   expected={'armeabi-v7a':'armv7l','armeabi':'armv7l','arm64-v8a':'aarch64','x86':'i686','x86_64':'x86_64'}.get(abi)
   sh='error() { exit 19; }; getprop2() { printf "%s" "$TEST_ABI"; };\n'+TARGET
   p=subprocess.run(['sh','-c',sh],env={**os.environ,'TEST_ABI':abi,'GAPPS_ARCH':package,'SYSTEM_OUT':'/unused'},capture_output=True)
   assert (p.returncode==0)==(expected==package), (abi,package,p.returncode);n+=1
 return n
if __name__=='__main__':
 print(json.dumps({'target_abi_shell_controls':tests(),**prepare(pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]))}))
