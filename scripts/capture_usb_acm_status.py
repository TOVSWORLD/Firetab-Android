#!/usr/bin/env python3
"""Explicit bounded capture; current serial admission denied. Offline files are private fixtures."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import termios
import time
from usb_acm_frame import FRAME, receive

ROOT=Path(__file__).resolve().parents[1]
PROFILE=ROOT/'projects/firetabs-android/diagnostic-usb/host-profile.json'
CAP=len(FRAME)+1
FLAGS=os.O_NOFOLLOW|os.O_CLOEXEC

class CaptureError(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def frame_contract():
    profile=json.loads(PROFILE.read_text())
    if type(profile.get('schema')) is not int or profile.get('schema')!=1 or profile.get('serial_device_capture_admitted') is not False or profile.get('package_runtime_qualified') is not False:
        raise CaptureError('profile-not-admitted')
    header=ROOT/profile['source_header']
    if header!=ROOT/'projects/firetabs-android/diagnostic-usb/acm_serial.h':raise CaptureError('profile-source-invalid')
    raw=header.read_bytes()
    matches=re.findall(r'^static const char ft_serial_frame\[\]="((?:\\.|[^"\\])*)";$',raw.decode(),re.M)
    if len(matches)!=1:raise CaptureError('source-frame-invalid')
    emitted=json.loads('"'+matches[0]+'"').encode('ascii')
    if hashlib.sha256(raw).hexdigest()!=profile['source_header_sha256'] or emitted!=FRAME or profile['frame_bytes']!=len(FRAME) or profile['frame_sha256']!=hashlib.sha256(FRAME).hexdigest():
        raise CaptureError('source-frame-drift')
    return profile


def child_name(name):
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}',name):
        raise CaptureError('private-path-required')
    return name


def private_name(path):
    path=Path(os.path.abspath(path));out=ROOT/'out'
    if path.parent!=out or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}',path.name):
        raise CaptureError('private-path-required')
    return child_name(path.name)


def check_private(info,kind):
    if not kind(info.st_mode) or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:
        raise CaptureError('private-file-required')


def open_out():
    try:os.mkdir(ROOT/'out',0o700)
    except FileExistsError:pass
    return os.open(ROOT/'out',os.O_RDONLY|os.O_DIRECTORY|FLAGS)


def close_after_failure(fd,error,code):
    try:os.close(fd)
    except OSError:
        error.capture_cleanup=getattr(error,'capture_cleanup',[])+[code]


def open_fixture(outfd,name):
    child_name(name)
    fd=os.open(name,os.O_RDONLY|FLAGS,dir_fd=outfd)
    try:
        info=os.fstat(fd);check_private(info,stat.S_ISREG)
        if info.st_size>CAP:raise CaptureError('input-byte-budget')
        return fd,info
    except BaseException as error:
        close_after_failure(fd,error,'input-close-error');raise


def read_selector(outfd,name):
    child_name(name)
    fd=os.open(name,os.O_RDONLY|FLAGS,dir_fd=outfd)
    try:
        info=os.fstat(fd);check_private(info,stat.S_ISREG)
        if not 1<=info.st_size<=128:raise CaptureError('selector-invalid')
        data=bytearray()
        for _ in range(16):
            try:chunk=os.read(fd,129-len(data))
            except InterruptedError:continue
            if not chunk:break
            data.extend(chunk)
            if len(data)>128:raise CaptureError('selector-invalid')
        else:raise CaptureError('selector-read-budget')
        try:endpoint=bytes(data).decode('ascii')
        except UnicodeDecodeError:raise CaptureError('selector-invalid') from None
        if not re.fullmatch(r'/dev/(?:ttyACM[0-9]{1,6}|cu\.usbmodem[A-Za-z0-9._-]{1,80})\n',endpoint):
            raise CaptureError('selector-invalid')
        after=os.fstat(fd)
        if (after.st_size,after.st_mtime_ns,after.st_ctime_ns)!=(info.st_size,info.st_mtime_ns,info.st_ctime_ns):
            raise CaptureError('selector-changed')
        result=endpoint[:-1]
    except BaseException as error:
        close_after_failure(fd,error,'selector-close-error');raise
    os.close(fd) # No retry after close errors.
    return result


def host_raw_settings(attrs):
    if len(attrs)!=7 or attrs[0]!=0 or attrs[1]!=0 or attrs[3]!=0:
        raise CaptureError('host-raw-tty-required')
    control=attrs[2]
    forbidden=termios.PARENB|termios.PARODD|termios.CSTOPB|termios.HUPCL|getattr(termios,'CRTSCTS',0)
    if control&termios.CSIZE!=termios.CS8 or control&forbidden or control&(termios.CREAD|termios.CLOCAL)!=(termios.CREAD|termios.CLOCAL):
        raise CaptureError('host-raw-tty-required')
    if attrs[4]!=termios.B9600 or attrs[5]!=termios.B9600:raise CaptureError('host-raw-tty-required')
    def cc(index):
        value=attrs[6][index]
        return value[0] if isinstance(value,bytes) and len(value)==1 else value
    if cc(termios.VMIN)!=1 or cc(termios.VTIME)!=0:raise CaptureError('host-raw-tty-required')


def open_serial(endpoint,*,admitted=False):
    if admitted is not True:raise CaptureError('serial-not-admitted')
    if not re.fullmatch(r'/dev/(?:ttyACM[0-9]{1,6}|cu\.usbmodem[A-Za-z0-9._-]{1,80})',endpoint):
        raise CaptureError('selector-invalid')
    fd=os.open(endpoint,os.O_RDONLY|os.O_NONBLOCK|os.O_NOCTTY|FLAGS)
    try:
        info=os.fstat(fd)
        if not stat.S_ISCHR(info.st_mode) or not os.isatty(fd):raise CaptureError('serial-character-tty-required')
        host_raw_settings(termios.tcgetattr(fd)) # Read-only verification; never configure the host TTY here.
        return fd,info
    except BaseException as error:
        close_after_failure(fd,error,'input-close-error');raise


def create_private(dirfd,name):
    if name not in ['raw.bin','private-receipt.json']:raise CaptureError('artifact-name-invalid')
    fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|FLAGS,0o600,dir_fd=dirfd)
    info=None
    try:
        info=os.fstat(fd);os.fchmod(fd,0o600);check_private(os.fstat(fd),stat.S_ISREG)
        return fd,info
    except BaseException as error:
        close_after_failure(fd,error,'artifact-close-error')
        if info is not None:
            try:unlink_owned(dirfd,name,info)
            except (OSError,CaptureError):error.capture_cleanup=getattr(error,'capture_cleanup',[])+['artifact-unlink-error']
        raise


def write_all(fd,data,on_written=lambda b:None):
    sent=0
    for _ in range(256):
        if sent==len(data):return
        try:n=os.write(fd,data[sent:])
        except InterruptedError:continue
        except BlockingIOError:raise CaptureError('artifact-write-error') from None
        if not isinstance(n,int) or n<=0 or n>len(data)-sent:raise CaptureError('artifact-short-write')
        on_written(data[sent:sent+n]);sent+=n
    raise CaptureError('artifact-write-budget')


def unlink_owned(dirfd,name,info):
    current=os.stat(name,dir_fd=dirfd,follow_symlinks=False)
    if (current.st_dev,current.st_ino)!=(info.st_dev,info.st_ino):raise CaptureError('artifact-ownership-changed')
    os.unlink(name,dir_fd=dirfd)


def failure_code(error):
    if isinstance(error,CaptureError):return error.code
    if isinstance(error,TimeoutError):return 'capture-timeout'
    if isinstance(error,KeyboardInterrupt):return 'interrupted'
    if isinstance(error,ValueError):return 'frame-invalid'
    if isinstance(error,OSError):return 'io-error'
    return 'capture-error'


def capture(input_path,output,*,serial=False,explicit_serial=False,timeout=1.0):
    """Never grant device/runtime qualification. Failed raw bytes stay private."""
    profile=frame_contract()
    if serial and (not explicit_serial or not profile['serial_device_capture_admitted']):
        raise CaptureError('serial-not-admitted') # Before selector/device/output opens.
    if not 0<timeout<=5:raise CaptureError('capture-policy-invalid')
    input_name=private_name(input_path);output_name=private_name(output)
    if input_name==output_name:raise CaptureError('output-must-be-new')
    outfd=open_out();dirfd=None;inputfd=None;rawfd=None;receipt=None
    digest=hashlib.sha256();written=0;observed=None;primary=None;cleanup=[];endpoint=None;info=None
    def accepted(chunk):
        nonlocal written
        digest.update(chunk);written+=len(chunk)
    try:
        os.mkdir(output_name,0o700,dir_fd=outfd) # Never adopt an existing capture directory.
        dirfd=os.open(output_name,os.O_RDONLY|os.O_DIRECTORY|FLAGS,dir_fd=outfd)
        os.fchmod(dirfd,0o700)
        rawfd,_=create_private(dirfd,'raw.bin')
        try:
            if serial:
                endpoint=read_selector(outfd,input_name);inputfd,info=open_serial(endpoint,admitted=profile['serial_device_capture_admitted'])
            else:inputfd,info=open_fixture(outfd,input_name)
            def read(count):
                chunk=os.read(inputfd,count)
                if not isinstance(chunk,bytes) or len(chunk)>count or written+len(chunk)>CAP:
                    raise CaptureError('input-byte-budget')
                if chunk:write_all(rawfd,chunk,accepted)
                return chunk
            observed=receive(read,time.monotonic,time.sleep,timeout=timeout)
            if not serial:
                if info.st_size!=observed['bytes']:raise CaptureError('input-extra-bytes')
                after=os.fstat(inputfd)
                if (after.st_size,after.st_mtime_ns,after.st_ctime_ns)!=(info.st_size,info.st_mtime_ns,info.st_ctime_ns):
                    raise CaptureError('input-changed')
        except (Exception,KeyboardInterrupt) as error:
            primary=failure_code(error);cleanup.extend(getattr(error,'capture_cleanup',[]))
        finally:
            if inputfd is not None:
                try:os.close(inputfd)
                except OSError:cleanup.append('input-close-error')
                inputfd=None
            try:os.fsync(rawfd)
            except OSError:cleanup.append('raw-sync-error')
            try:os.close(rawfd)
            except OSError:cleanup.append('raw-close-error')
            rawfd=None
        ok=observed is not None and primary is None and not cleanup
        receipt={'schema':1,'kind':'serial' if serial else 'offline-fixture','ok':ok,
                 'frame_validated':ok,'host_frame_observed':bool(ok and serial),
                 'raw_bytes':written,'raw_sha256':digest.hexdigest() if ok else None,
                 'expected_frame_sha256':profile['frame_sha256'],'source_header_sha256':profile['source_header_sha256'],
                 'failure':primary or (cleanup[0] if cleanup else None),'cleanup':cleanup,'boot_qualified':False,'runtime_qualified':False}
        # This file is private; stdout never contains the selector or endpoint.
        private={**receipt,'raw_sha256':digest.hexdigest(),'input_file':str(input_path),'endpoint':endpoint,
                 'final_descriptor_teardown_pending':True}
        reportfd=None;reportinfo=None
        try:
            reportfd,reportinfo=create_private(dirfd,'private-receipt.json')
            write_all(reportfd,(json.dumps(private,indent=2)+'\n').encode())
            os.fsync(reportfd)
            closefd=reportfd;reportfd=None;os.close(closefd)
            os.fsync(dirfd);os.fsync(outfd)
        except (Exception,KeyboardInterrupt) as error:
            cleanup.extend(getattr(error,'capture_cleanup',[]))
            if reportfd is not None:
                try:os.close(reportfd)
                except OSError:pass
            if reportinfo is not None:
                try:unlink_owned(dirfd,'private-receipt.json',reportinfo)
                except OSError:cleanup.append('receipt-unlink-error')
                except CaptureError:cleanup.append('receipt-ownership-changed')
            receipt.update(ok=False,frame_validated=False,host_frame_observed=False,raw_sha256=None,
                           failure=primary or failure_code(error),cleanup=cleanup+['receipt-incomplete'])
        return receipt
    finally:
        for fd in [inputfd,rawfd,dirfd,outfd]:
            if fd is not None:
                try:os.close(fd)
                except OSError:
                    if receipt is not None:
                        receipt.update(ok=False,frame_validated=False,host_frame_observed=False,raw_sha256=None,
                                       failure=receipt['failure'] or 'directory-close-error')
                        receipt['cleanup'].append('directory-close-error') # Never retry a failed close.


class Parser(argparse.ArgumentParser):
    def error(self,message):raise CaptureError('arguments-invalid')


def main(argv=None):
    parser=Parser(prog='firetabs-acm-capture',description=__doc__)
    inputs=parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--input-file',type=Path)
    inputs.add_argument('--serial-selector',type=Path)
    parser.add_argument('--allow-read-only-serial',action='store_true')
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--timeout',type=float,default=1.0)
    try:
        args=parser.parse_args(argv)
        if args.allow_read_only_serial and args.serial_selector is None:raise CaptureError('arguments-invalid')
        result=capture(args.serial_selector or args.input_file,args.output,serial=args.serial_selector is not None,
                       explicit_serial=args.allow_read_only_serial,timeout=args.timeout)
    except (Exception,KeyboardInterrupt) as error:
        result={'ok':False,'failure':failure_code(error),'cleanup':getattr(error,'capture_cleanup',[]),'boot_qualified':False,'runtime_qualified':False}
    print(json.dumps(result,sort_keys=True))
    return 0 if result['ok'] else 130 if result.get('failure')=='interrupted' else 1

if __name__=='__main__':sys.exit(main())
