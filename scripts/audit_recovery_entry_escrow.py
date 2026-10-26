#!/usr/bin/env python3
"""AST-only entry/escrow audit of cached sources; never import or execute them."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def functions(source):
    tree=ast.parse(source)
    return tree,{node.name:node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)}


def calls(node):
    return sorted([{'callee':ast.unparse(x.func),'line':x.lineno} for x in ast.walk(node)
                   if isinstance(x,ast.Call)],key=lambda x:x['line'])


def archive_facts(source):
    _,func=functions(source)
    main=calls(func['main'])
    writes=[x for x in main if x['callee'] in {'flash_data','flash_binary','dev.rpmb_write'}]
    if not writes:raise ValueError('Expected persistent operations missing; source changed')
    dump=[x for x in main if x['callee']=='dump_binary']
    for origin,destination in [('main','switch_user'),('switch_user','flash_binary'),('flash_binary','flash_data'),('flash_data','dev.emmc_write')]:
        if destination not in {x['callee'] for x in calls(func[origin])}:
            raise ValueError('Expected conditional storage-write path differs')
    flash=calls(func['flash_binary'])
    bound_dropped=False
    for node in ast.walk(func['flash_binary']):
        if isinstance(node,ast.Call) and ast.unparse(node.func)=='flash_data':
            bound_dropped=any(k.arg=='max_size' and isinstance(k.value,ast.Constant) and k.value.value==0 for k in node.keywords)
    linux_proc=any(isinstance(x,ast.Call) and ast.unparse(x.func)=='os.listdir' and
                   x.args and isinstance(x.args[0],ast.Constant) and x.args[0].value=='/proc'
                   for x in ast.walk(func['check_modemmanager']))
    return {'main_persistent_operation_sites':writes,'main_explicit_dump_calls':dump,
            'complete_backup_before_first_write_established':False,
            'conditional_early_write_path':['main','switch_user','flash_binary','flash_data','device storage write'],
            'conditional_early_write_modes':['fix16','fix32'],
            'flash_helper_forwards_requested_size_limit':not bound_dropped,
            'linux_proc_assumption':linux_proc,'minimal_mode_is_read_only':False,
            'ram_payload_entry_and_mmio_safety_verified':False}


def modern_facts(config,handler,install):
    tree=ast.parse(config)
    chip=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Dict):
            for key,value in zip(node.keys,node.values):
                if isinstance(key,ast.Constant) and key.value==0x8163 and isinstance(value,ast.Call):
                    fields={k.arg:k.value.value for k in value.keywords if isinstance(k.value,ast.Constant)}
                    chip.append({'name':fields.get('name'),'dacode_matches_mt8163':fields.get('dacode')==0x8163,
                                 'dedicated_loader_reference_present':bool(fields.get('loader')),'line':value.lineno})
    if len(chip)!=1 or chip[0]['name']!='MT8163':raise ValueError('Dedicated MT8163 config missing')
    _,func=functions(handler)
    read_paths={name:[x for x in calls(func[name]) if x['callee'].endswith(('.readflash','.writeflash','.formatflash'))]
                for name in ['da_read','da_rf','da_rl']}
    cfg=calls(func['configure_da'])
    writes=[x for x in cfg if x['callee'].endswith(('.writeflash','.formatflash','.write_rpmb'))]
    gpt_nodes=list(ast.walk(func['da_rl']))
    gpt_names={x.value for x in gpt_nodes if isinstance(x,ast.Constant) and isinstance(x.value,str)}
    same_data=sum(1 for x in gpt_nodes if isinstance(x,ast.Call) and ast.unparse(x.func)=='wf.write' and
                  len(x.args)==1 and isinstance(x.args[0],ast.Name) and x.args[0].id=='data')>=2
    duplicate_gpt= {'gpt.bin','gpt_backup.bin'}.issubset(gpt_names) and same_data
    source_lines=handler.splitlines()
    backup_lines=[i+1 for i,line in enumerate(source_lines) if 'gpt_backup.bin' in line]
    return {'dedicated_soc_config':chip[0],'read_entry_paths':read_paths,
            'configure_da_direct_storage_write_calls':writes,
            'configure_da_requires_bootstrap_and_ram_agent':True,
            'configure_da_host_state_write_present':any(x['callee'].endswith('.writestate') for x in cfg),
            'bootstrap_indirect_effects_audited':False,
            'all_read_operations_globally_persistence_free':False,
            'gpt_backup_filename_lines':backup_lines,
            'gpt_backup_independent_capture_verified':False,
            'gpt_same_data_write_observed':duplicate_gpt,
            'gpt_backup_observation':'Do not assume independently captured secondary GPT from a backup filename; validate raw secondary header/CRC separately',
            'macos_documentation_present':'### macOS' in install,
            'apple_silicon_documentation_present':'Apple Silicon' in install,
            'macos_runtime_or_device_support_verified':False,'dependencies_installed':False}


def main():
    index=json.loads((ROOT/'evidence/recovery-entry-escrow/source-index.json').read_text())
    loaded={}
    for record in index['files']:
        path=ROOT/'out/recovery-entry/mtkclient'/record['source_path']
        raw=path.read_bytes()
        if len(raw)!=record['bytes'] or hashlib.sha256(raw).hexdigest()!=record['sha256']:
            raise ValueError('Cached candidate source hash mismatch')
        loaded[record['source_path']]=raw.decode()
    archive=(ROOT/'out/recovery-provenance/extracted/amonet/modules/main.py').read_bytes()
    if hashlib.sha256(archive).hexdigest()!=index['archived_main_sha256']:
        raise ValueError('Cached archive source hash mismatch')
    result={'scope':'Static source facts and possible alternative only; no device/helper/payload execution',
            'archive':archive_facts(archive.decode()),
            'modern_candidate':modern_facts(loaded['mtkclient/config/brom_config.py'],
                loaded['mtkclient/Library/DA/mtk_da_handler.py'],loaded['README-INSTALL.md']),
            'qualification':'NOT_READY: entry/bootstrap, independent escrow, restore and host USB behavior remain unverified',
            'physical_test_ready':False,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
