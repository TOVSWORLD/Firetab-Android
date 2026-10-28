#!/usr/bin/env python3
"""Check the bounded LK source packet without upgrading any runtime gate."""
import argparse
import hashlib
import json
from pathlib import Path
from trace_lk_dtb_selection import LK_SHA

ROOT=Path(__file__).resolve().parents[1]
IDS={'entry-and-smc','header-and-inflate','bootargs','dtb-selection','dtb-destination',
     'memory-tuples','entry-pointer','alternate-and-idme','cpu-mutation'}
GATES={'installed_identity','bounded_entry','matching_final_dtb','independent_return','failure_log'}


def validate(packet,root=ROOT):
    if packet.get('schema_version')!=1 or packet.get('issue')!=347 or packet.get('lk_sha256')!=LK_SHA:
        raise ValueError('Wrong source packet identity')
    if packet.get('ready_for_loading_trial') is not False or packet.get('beta_ready') is not False:
        raise ValueError('Source inventory cannot claim loading/beta admission')
    gates=packet.get('runtime_gates',{})
    if set(gates)!=GATES or any(g.get('qualified') is not False or not g.get('required_evidence') for g in gates.values()):
        raise ValueError('All five runtime gates must remain explicitly unqualified')
    receipts=packet.get('receipts',[])
    if len(receipts)!=len(IDS) or {r.get('id') for r in receipts}!=IDS:
        raise ValueError('Incomplete/duplicate source coverage')
    seen=set()
    for row in receipts:
        relative=Path(row['evidence'])
        if relative.is_absolute() or '..' in relative.parts or len(relative.parts)!=3 or relative.parts[0]!='evidence' or relative.name!='report.json':
            raise ValueError('Receipt must be a repository evidence/report.json')
        if str(relative) in seen:raise ValueError('Repeated evidence receipt')
        seen.add(str(relative))
        raw=(root/relative).read_bytes()
        if len(raw)>131072 or hashlib.sha256(raw).hexdigest()!=row['receipt_sha256']:
            raise ValueError('Receipt content/hash changed: '+str(relative))
        report=json.loads(raw)
        if report.get('lk_sha256')!=LK_SHA or row.get('lk_sha256')!=LK_SHA or not row.get('source_result'):
            raise ValueError('Cross-artifact or missing coverage claim')
    if not packet.get('source_open_items') or not packet.get('privacy') or not packet.get('next_executable_source_acceptance'):
        raise ValueError('Missing unresolved/privacy/next acceptance')
    return {'source_packet_consistent':True,'receipts_checked':len(receipts),
            'qualified_runtime_gates':0,'ready_for_loading_trial':False,'beta_ready':False}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,default=ROOT/'evidence/lk-handoff-coverage/manifest.json');args=p.parse_args()
    print(json.dumps(validate(json.loads(args.manifest.read_text())),indent=2))


if __name__=='__main__':main()
