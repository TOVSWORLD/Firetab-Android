#!/usr/bin/env python3
"""Pinned syntax-only entry audit; no imports or execution of candidate helpers."""
import ast
import hashlib
import json
from pathlib import Path
from audit_recovery_entry_escrow import functions,calls

ROOT=Path(__file__).resolve().parents[1]
FILES=('mtkclient/Library/mtk_class.py','mtkclient/Library/mtk_preloader.py',
       'mtkclient/Library/pltools.py','mtkclient/config/mtk_config.py','mtkclient/config/brom_config.py')


def main():
    index=json.loads((ROOT/'evidence/mac-cli-imports/report.json').read_text())
    expected={x['path']:x for x in index['modules']};loaded={};receipts=[]
    for name in FILES:
        raw=(ROOT/'out/recovery-entry/mtkclient'/name).read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if digest!=expected[name]['sha256']:raise ValueError('Pinned helper source mismatch')
        loaded[name]=raw.decode();receipts.append({'path':name,'sha256':digest,
          'url':f"https://github.com/bkerler/mtkclient/blob/{index['revision']}/{name}"})
    _,mtk=functions(loaded[FILES[0]]);_,preloader=functions(loaded[FILES[1]]);_,tools=functions(loaded[FILES[2]])
    selected={
      'crasher':[x for x in calls(mtk['crasher']) if x['callee'] in ('plt.crash','rmtk.preloader.init')],
      'bypass_security':[x for x in calls(mtk['bypass_security']) if x['callee'] in ('self.crasher','plt.runpayload')],
      'preloader_init':[x for x in calls(preloader['init']) if x['callee'] in (
          'self.setreg_disablewatchdogtimer','self.get_target_config','self.get_hw_sw_ver',
          'self.get_meid','self.get_socid','self.config.hwparam.writesetting','os.remove')],
      'reset_to_brom':[x for x in calls(preloader['reset_to_brom']) if x['callee'].endswith('.write32')],
      'crash_delegate':calls(tools['crash'])}
    guard=next(n for n in ast.walk(mtk['crasher']) if isinstance(n,ast.If) and
        any(isinstance(x,ast.Attribute) and x.attr=='enforcecrash' for x in ast.walk(n.test)))
    watchdog=next(n for n in ast.walk(preloader['init']) if isinstance(n,ast.If) and
        any(isinstance(x,ast.Name) and x.id=='skipwdt' for x in ast.walk(n.test)))
    result={'scope':'Selected pinned source paths only; no whole-bootstrap side-effect qualification',
        'revision':index['revision'],'sources':receipts,'selected_call_sites':selected,
        'crasher_entry_condition':ast.unparse(guard.test),'watchdog_call_condition':ast.unparse(watchdog.test),
        'crasher_terminal_return_is_brom_assertion':False,
        'preloader_initialization_is_passive_usb_enumeration':False,
        'host_identifier_logs_require_separate_sanitization':True,
        'globally_persistence_free_bootstrap_verified':False,
        'usb_only_transition_verified_for_installed_state':False,
        'hardware_access_mandatory_proven':False,'physical_test_ready':False,
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
