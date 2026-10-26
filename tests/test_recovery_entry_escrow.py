from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_recovery_entry_escrow import archive_facts,modern_facts

ARCHIVE='''
def main():
    switch_user(dev)
    flash_data(dev,data,0)
    dev.rpmb_write(data)
def switch_user(dev):
    if fix16: flash_binary(dev,path,0)
def flash_binary(dev,path,start,max_size=0):
    flash_data(dev,data,start,max_size=0)
def flash_data(dev,data,start,max_size=0):
    dev.emmc_write(start,data)
def check_modemmanager():
    os.listdir('/proc')
'''
HANDLER='''
def configure_da(self,mtk):
    mtk.bypass_security()
    mtk.daloader.upload_da()
    mtk.daloader.writestate()
def da_read(self): self.mtk.daloader.readflash()
def da_rf(self): self.mtk.daloader.readflash()
def da_rl(self):
    first='gpt.bin'
    second='gpt_backup.bin'
    wf.write(data)
    wf.write(data)
'''


class EntryEscrowAudit(unittest.TestCase):
    def test_archive_boundary_and_hidden_write_are_not_read_only(self):
        result=archive_facts(ARCHIVE)
        self.assertFalse(result['minimal_mode_is_read_only'])
        self.assertFalse(result['complete_backup_before_first_write_established'])
        self.assertFalse(result['flash_helper_forwards_requested_size_limit'])
        self.assertTrue(result['linux_proc_assumption'])
        with self.assertRaises(ValueError):archive_facts(ARCHIVE.replace('dev.emmc_write','dev.read_only'))

    def test_modern_read_dispatch_does_not_qualify_bootstrap(self):
        config='chip={0x8163:Chipconfig(name="MT8163",dacode=0x8163,loader="reference")}'
        result=modern_facts(config,HANDLER,'### macOS\nApple Silicon')
        self.assertTrue(result['dedicated_soc_config']['dacode_matches_mt8163'])
        self.assertTrue(result['gpt_same_data_write_observed'])
        self.assertTrue(result['configure_da_host_state_write_present'])
        self.assertFalse(result['bootstrap_indirect_effects_audited'])
        self.assertFalse(result['all_read_operations_globally_persistence_free'])
        self.assertFalse(result['macos_runtime_or_device_support_verified'])
        with self.assertRaises(ValueError):modern_facts('chip={}',HANDLER,'')
