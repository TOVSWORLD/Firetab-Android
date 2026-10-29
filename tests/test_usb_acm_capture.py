from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import capture_usb_acm_status as capture
from usb_acm_frame import FRAME

class Capture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.out=self.root/'out';self.out.mkdir(mode=0o700)
        source=self.root/'projects/firetabs-android/diagnostic-usb';source.mkdir(parents=True)
        for name in ['host-profile.json','acm_serial.h']:shutil.copyfile(ROOT/'projects/firetabs-android/diagnostic-usb'/name,source/name)
        self.addCleanup(patch.stopall)
        patch.object(capture,'ROOT',self.root).start();patch.object(capture,'PROFILE',source/'host-profile.json').start()
        self.fixture=self.out/'private-fixture';self.fixture.write_bytes(FRAME);self.fixture.chmod(0o600)
    def raw_settings(self):
        t=capture.termios;cc=[0]*max(t.NCCS,t.VMIN+1,t.VTIME+1);cc[t.VMIN]=1
        return [0,0,t.CS8|t.CREAD|t.CLOCAL,0,t.B9600,t.B9600,cc]
    def run_capture(self,name='capture'):
        return capture.capture(self.fixture,self.out/name)
    def test_offline_real_files_permissions_and_no_false_host_observation(self):
        result=self.run_capture();self.assertTrue(result['ok']);self.assertFalse(result['host_frame_observed']);self.assertFalse(result['runtime_qualified']);self.assertEqual(result['kind'],'offline-fixture')
        folder=self.out/'capture';self.assertEqual(stat.S_IMODE(folder.stat().st_mode),0o700)
        for name in ['raw.bin','private-receipt.json']:self.assertEqual(stat.S_IMODE((folder/name).stat().st_mode),0o600)
        self.assertEqual((folder/'raw.bin').read_bytes(),FRAME)
        private=json.loads((folder/'private-receipt.json').read_text());self.assertEqual(private['input_file'],str(self.fixture));self.assertTrue(private['final_descriptor_teardown_pending'])
        self.assertNotIn('input_file',result);self.assertNotIn('endpoint',result)
    def test_invalid_raw_retained_privately_hash_not_published(self):
        self.fixture.write_bytes(b'PRIVATE-HOUSEHOLD-SELECTOR\n')
        result=self.run_capture();self.assertFalse(result['ok']);self.assertEqual(result['failure'],'frame-invalid');self.assertIsNone(result['raw_sha256'])
        self.assertEqual((self.out/'capture/raw.bin').read_bytes(),self.fixture.read_bytes())
        private=json.loads((self.out/'capture/private-receipt.json').read_text());self.assertIsNotNone(private['raw_sha256']);self.assertNotIn('PRIVATE-HOUSEHOLD',json.dumps(result))
    def test_existing_outputs_and_symlinks_never_adopted(self):
        self.run_capture();sentinel=self.out/'capture/sentinel';sentinel.write_text('keep')
        with self.assertRaises(FileExistsError):self.run_capture()
        self.assertEqual(sentinel.read_text(),'keep')
        link=self.out/'fixture-link';link.symlink_to(self.fixture)
        result=capture.capture(link,self.out/'link-attempt');self.assertFalse(result['ok'])
        outside=self.root/'outside';outside.mkdir();(self.out/'output-link').symlink_to(outside)
        with self.assertRaises(FileExistsError):capture.capture(self.fixture,self.out/'output-link')
        self.assertEqual(list(outside.iterdir()),[])
    def test_public_or_linked_or_nonregular_inputs_rejected(self):
        self.fixture.chmod(0o644);result=self.run_capture('public');self.assertEqual(result['failure'],'private-file-required')
        self.fixture.chmod(0o600);os.link(self.fixture,self.out/'hardlink');result=self.run_capture('linked');self.assertEqual(result['failure'],'private-file-required')
        with self.assertRaises(capture.CaptureError):capture.private_name(self.root/'not-private')
        with self.assertRaises(capture.CaptureError):capture.private_name(self.out/'nested/file')
    def test_input_budget_and_metadata_change_rejected(self):
        self.fixture.write_bytes(FRAME+b'xx');self.assertEqual(self.run_capture('large')['failure'],'input-byte-budget')
        self.fixture.write_bytes(FRAME);original=os.fstat;seen=0
        def changed(fd):
            nonlocal seen
            info=original(fd)
            if stat.S_ISREG(info.st_mode) and info.st_size==len(FRAME):
                seen+=1
                if seen==2:return SimpleNamespace(st_size=info.st_size+1,st_mtime_ns=info.st_mtime_ns,st_ctime_ns=info.st_ctime_ns)
            return info
        with patch.object(capture.os,'fstat',changed):self.assertEqual(self.run_capture('changed')['failure'],'input-changed')
    def test_short_file_read_cannot_hide_trailing_offline_data(self):
        self.fixture.write_bytes(FRAME+b'x');original=os.read
        def short_read(fd,n):return original(fd,min(n,len(FRAME)))
        with patch.object(capture.os,'read',short_read):result=self.run_capture('trailing-hidden')
        self.assertFalse(result['ok']);self.assertEqual(result['failure'],'input-extra-bytes');self.assertFalse(result['host_frame_observed'])
    def test_partial_and_eintr_artifact_writes(self):
        original=os.write;calls=0
        def partial(fd,data):
            nonlocal calls
            calls+=1
            if calls<3:raise InterruptedError()
            return original(fd,data[:7])
        with patch.object(capture.os,'write',partial):result=self.run_capture()
        self.assertTrue(result['ok']);self.assertGreater(calls,10);self.assertEqual((self.out/'capture/raw.bin').read_bytes(),FRAME)
    def test_short_write_and_incomplete_receipt_cleanup(self):
        original=os.write
        def zero_raw(fd,data):
            if data.startswith(b'FIRETABS'):return 0
            return original(fd,data)
        with patch.object(capture.os,'write',zero_raw):result=self.run_capture('short')
        self.assertEqual(result['failure'],'artifact-short-write');self.assertEqual((self.out/'short/raw.bin').read_bytes(),b'')
        def receipt_error(fd,data):
            if data.startswith(b'{'):raise OSError('PRIVATE-ENDPOINT')
            return original(fd,data)
        with patch.object(capture.os,'write',receipt_error):result=self.run_capture('report-failed')
        self.assertFalse(result['ok']);self.assertEqual(result['cleanup'],['receipt-incomplete']);self.assertFalse((self.out/'report-failed/private-receipt.json').exists());self.assertEqual((self.out/'report-failed/raw.bin').read_bytes(),FRAME)
    def test_primary_error_preserved_with_close_error_no_retry(self):
        self.fixture.write_bytes(b'bad');original=os.close;calls={}
        def close_once(fd):
            calls[fd]=calls.get(fd,0)+1
            original(fd)
            if calls[fd]==1 and fd==self.inputfd:raise InterruptedError()
        original_open=os.open;self.inputfd=-1
        def opened(path,*args,**kwargs):
            fd=original_open(path,*args,**kwargs)
            if path=='private-fixture':self.inputfd=fd
            return fd
        with patch.object(capture.os,'open',opened),patch.object(capture.os,'close',close_once):result=self.run_capture()
        self.assertEqual(result['failure'],'frame-invalid');self.assertIn('input-close-error',result['cleanup']);self.assertEqual(calls[self.inputfd],1)
    def test_receipt_ownership_change_not_deleted(self):
        original_write=os.write;original_unlink=capture.unlink_owned
        def bad_receipt(fd,data):
            if data.startswith(b'{'):raise OSError('write failure')
            return original_write(fd,data)
        def replaced(dirfd,name,info):
            os.rename(self.out/'capture/private-receipt.json',self.out/'capture/old-owned')
            (self.out/'capture/private-receipt.json').write_text('unrelated')
            return original_unlink(dirfd,name,info)
        with patch.object(capture.os,'write',bad_receipt),patch.object(capture,'unlink_owned',replaced):result=self.run_capture()
        self.assertFalse(result['ok']);self.assertIn('receipt-ownership-changed',result['cleanup']);self.assertEqual((self.out/'capture/private-receipt.json').read_text(),'unrelated')
    def test_cli_privacy_and_serial_denied_before_opens(self):
        secret=self.out/'HOUSEHOLD-SECRET';secret.write_text('/dev/ttyACM987\n');secret.chmod(0o600)
        for explicit in [False,True]:
            argv=['--serial-selector',str(secret),'--output',str(self.out/'denied')]+(['--allow-read-only-serial'] if explicit else [])
            stream=io.StringIO()
            with patch.object(capture.os,'open',side_effect=AssertionError('unexpected open')),redirect_stdout(stream):code=capture.main(argv)
            self.assertEqual(code,1);self.assertEqual(json.loads(stream.getvalue())['failure'],'serial-not-admitted');self.assertNotIn('HOUSEHOLD',stream.getvalue());self.assertNotIn('ttyACM',stream.getvalue())
        stream=io.StringIO()
        with redirect_stdout(stream):code=capture.main(['--input-file',str(self.fixture),'--output',str(self.out/'cli')])
        self.assertEqual(code,0);self.assertNotIn(str(self.root),stream.getvalue());self.assertFalse(json.loads(stream.getvalue())['host_frame_observed'])
    def test_artifact_eagain_is_not_misclassified_as_input_retry(self):
        original=os.write;reads=0;original_read=os.read
        def blocked(fd,data):
            if data.startswith(b'FIRETABS'):raise BlockingIOError()
            return original(fd,data)
        def read(fd,n):
            nonlocal reads
            reads+=1;return original_read(fd,n)
        with patch.object(capture.os,'write',blocked),patch.object(capture.os,'read',read):result=self.run_capture('artifact-eagain')
        self.assertEqual(result['failure'],'artifact-write-error');self.assertEqual(reads,1)
        with patch.object(capture.os,'open') as opened:
            with self.assertRaises(capture.CaptureError):capture.read_selector(91,'../escape')
            opened.assert_not_called()
    def test_source_frame_and_profile_drift_rejected(self):
        header=self.root/'projects/firetabs-android/diagnostic-usb/acm_serial.h';header.write_text(header.read_text()+'\n/* drift */\n')
        with self.assertRaises(capture.CaptureError):capture.frame_contract()
        shutil.copyfile(ROOT/'projects/firetabs-android/diagnostic-usb/acm_serial.h',header)
        profile=json.loads(capture.PROFILE.read_text());profile['serial_device_capture_admitted']=True;capture.PROFILE.write_text(json.dumps(profile))
        with self.assertRaises(capture.CaptureError):capture.frame_contract()
    def test_read_only_serial_adapter_mock_flags_and_type(self):
        flags=[]
        def opened(endpoint,value):flags.append(value);self.assertEqual(endpoint,'/dev/ttyACM42');return 78
        with patch.object(capture.os,'open',opened),patch.object(capture.os,'fstat',return_value=SimpleNamespace(st_mode=stat.S_IFCHR)),patch.object(capture.os,'isatty',return_value=True),patch.object(capture.termios,'tcgetattr',return_value=self.raw_settings()):
            fd,info=capture.open_serial('/dev/ttyACM42',admitted=True);self.assertEqual(fd,78)
        expected=os.O_NONBLOCK|os.O_NOCTTY|os.O_NOFOLLOW|os.O_CLOEXEC
        self.assertEqual(flags,[os.O_RDONLY|expected]);self.assertFalse(flags[0]&(os.O_WRONLY|os.O_RDWR))
        with patch.object(capture.os,'open') as opened:
            with self.assertRaises(capture.CaptureError):capture.open_serial('/dev/ttyACM42')
            opened.assert_not_called()
        with patch.object(capture.os,'open',return_value=78),patch.object(capture.os,'fstat',return_value=SimpleNamespace(st_mode=stat.S_IFBLK)),patch.object(capture.os,'close') as close:
            with self.assertRaises(capture.CaptureError):capture.open_serial('/dev/ttyACM42',admitted=True)
            close.assert_called_once_with(78)
    def test_host_raw_settings_read_only_and_reject_transforms(self):
        attrs=self.raw_settings();capture.host_raw_settings(attrs)
        for index,value in [(0,1),(1,1),(3,1),(4,0),(5,0)]:
            changed=self.raw_settings();changed[index]=value
            with self.assertRaises(capture.CaptureError):capture.host_raw_settings(changed)
        attrs=self.raw_settings();attrs[2]|=capture.termios.HUPCL
        with self.assertRaises(capture.CaptureError):capture.host_raw_settings(attrs)
        attrs=self.raw_settings();attrs[6][capture.termios.VTIME]=1
        with self.assertRaises(capture.CaptureError):capture.host_raw_settings(attrs)
    def test_sync_failure_and_directory_close_error_never_report_success(self):
        original=capture.os.fsync;calls=0
        def fail_first(fd):
            nonlocal calls
            calls+=1
            if calls==1:raise OSError('raw sync failure')
            return original(fd)
        with patch.object(capture.os,'fsync',fail_first):result=self.run_capture('sync-failed')
        self.assertFalse(result['ok']);self.assertEqual(result['failure'],'raw-sync-error');self.assertTrue((self.out/'sync-failed/raw.bin').exists())
        original_open=os.open;original_close=os.close;directory=-1;closes=0
        def opened(path,*args,**kwargs):
            nonlocal directory
            fd=original_open(path,*args,**kwargs)
            if path=='close-failed':directory=fd
            return fd
        def closed(fd):
            nonlocal closes
            original_close(fd)
            if fd==directory:closes+=1;raise InterruptedError()
        with patch.object(capture.os,'open',opened),patch.object(capture.os,'close',closed):result=self.run_capture('close-failed')
        self.assertFalse(result['ok']);self.assertEqual(result['failure'],'directory-close-error');self.assertEqual(closes,1)
    def test_actual_read_error_and_cli_argument_privacy(self):
        with patch.object(capture.os,'read',side_effect=OSError('PRIVATE-SELECTOR')):result=self.run_capture('read-failed')
        self.assertEqual(result['failure'],'io-error');self.assertNotIn('PRIVATE',json.dumps(result))
        stream=io.StringIO()
        with redirect_stdout(stream):code=capture.main(['--HOUSEHOLD-SECRET'])
        self.assertEqual(code,1);self.assertNotIn('HOUSEHOLD',stream.getvalue())
    def test_failed_private_file_preflight_removes_only_new_owned_file(self):
        original=os.fchmod
        def failed(fd,mode):
            if mode==0o600:raise OSError('file chmod failure')
            return original(fd,mode)
        with patch.object(capture.os,'fchmod',failed):
            with self.assertRaises(OSError):self.run_capture('preflight-failed')
        self.assertEqual(list((self.out/'preflight-failed').iterdir()),[]);self.assertEqual(self.fixture.read_bytes(),FRAME)
    def test_write_attempt_bound_and_zero_output_contract(self):
        with patch.object(capture.os,'write',side_effect=InterruptedError()) as write:
            with self.assertRaises(capture.CaptureError):capture.write_all(90,b'bounded')
            self.assertEqual(write.call_count,256)
        with patch.object(capture.os,'write',return_value=100):
            with self.assertRaises(capture.CaptureError):capture.write_all(90,b'bounded')
    def test_selector_private_bounded_and_allowlisted(self):
        path=self.out/'selector';path.write_text('/dev/cu.usbmodemTEST42\n');path.chmod(0o600);fd=os.open(self.out,os.O_RDONLY|os.O_DIRECTORY)
        try:
            self.assertEqual(capture.read_selector(fd,'selector'),'/dev/cu.usbmodemTEST42')
            for value in ['/dev/disk0\n','/dev/ttyACM1\n/dev/ttyACM2\n','/dev/ttyACM1','X'*129]:
                path.write_text(value)
                with self.assertRaises(capture.CaptureError):capture.read_selector(fd,'selector')
        finally:os.close(fd)

if __name__=='__main__':unittest.main()
