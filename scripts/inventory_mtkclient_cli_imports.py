#!/usr/bin/env python3
"""Pinned source-only conservative CLI import inventory; never import upstream."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
REV='7cb40e727727dfe3faa065eefb29b16ed29bbdf1'
FILE_CAP=192*1024
TOTAL_CAP=2*1024*1024


def imports(source):
    tree=ast.parse(source)
    result=[]
    def visit(node, guarded=False, deferred=False, main_guard=False):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            names=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or '']
            result.extend({'module':name,'line':node.lineno,'importerror_guard':guarded,
                           'deferred_scope':deferred,'relative':bool(getattr(node,'level',0)), 'main_guard':main_guard} for name in names)
        if isinstance(node,ast.Try):
            protects=any(handler.type and any(isinstance(x,ast.Name) and x.id=='ImportError'
                for x in ast.walk(handler.type)) for handler in node.handlers)
            for child in node.body:visit(child,guarded or protects,deferred,main_guard)
            for child in [*node.handlers,*node.orelse,*node.finalbody]:visit(child,guarded,deferred,main_guard)
            return
        if isinstance(node,ast.If) and isinstance(node.test,ast.Compare):
            test=node.test
            if (isinstance(test.left,ast.Name) and test.left.id=='__name__' and
                len(test.ops)==1 and isinstance(test.ops[0],ast.Eq) and
                isinstance(test.comparators[0],ast.Constant) and test.comparators[0].value=='__main__'):
                for child in node.body:visit(child,guarded,deferred,True)
                for child in node.orelse:visit(child,guarded,deferred,main_guard)
                return
        next_deferred=deferred or isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))
        for child in ast.iter_child_nodes(node):visit(child,guarded,next_deferred,main_guard)
    visit(tree)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-source',action='store_true')
    args=parser.parse_args()
    raw=(ROOT/'out/recovery-entry/mtkclient-tree.json').read_bytes()
    index=json.loads((ROOT/'evidence/recovery-agent/source-index.json').read_text())
    if hashlib.sha256(raw).hexdigest()!=index['tree_sha256']:
        raise ValueError('Pinned Git tree mismatch')
    tree=json.loads(raw)
    paths={x['path']:x for x in tree['tree'] if x['type']=='blob' and x['path'].endswith('.py')}
    pending=['mtk.py'];seen=set();modules=[];externals=[];unresolved=[];downloaded=0
    while pending:
        name=pending.pop()
        if name in seen:continue
        seen.add(name)
        if len(seen)>100:raise ValueError('Module-count cap exceeded')
        entry=paths[name];path=ROOT/'out/recovery-entry/mtkclient'/name
        if entry['size']>FILE_CAP:
            unresolved.append({'path':name,'reason':'per-source cap'});continue
        if not path.exists():
            if not args.fetch_source:
                unresolved.append({'path':name,'reason':'uncached'});continue
            if downloaded+entry['size']>TOTAL_CAP:
                unresolved.append({'path':name,'reason':'aggregate source cap'});continue
            url=f'https://raw.githubusercontent.com/bkerler/mtkclient/{REV}/{name}'
            with urllib.request.urlopen(url,timeout=25) as response:data=response.read(entry['size']+1)
            if len(data)!=entry['size']:raise ValueError('Wrong source response length')
            downloaded+=len(data)
            if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=entry['sha']:
                raise ValueError('Source Git blob identity mismatch')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        data=path.read_bytes()
        if len(data)!=entry['size'] or hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=entry['sha']:
            raise ValueError('Cached source identity mismatch')
        modules.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        for record in imports(data.decode()):
            mod=record['module']
            if record['relative']:
                unresolved.append({'path':name,'line':record['line'],'reason':'relative import not resolved'});continue
            if mod=='mtkclient' or mod.startswith('mtkclient.'):
                base=mod.replace('.','/')
                target=next((p for p in [base+'.py',base+'/__init__.py'] if p in paths),None)
                if target:pending.append(target)
                else:unresolved.append({'path':name,'line':record['line'],'reason':'unresolved package/module'})
            elif mod and mod.split('.')[0] not in sys.stdlib_module_names:
                externals.append({'source_path':name,**record})
    print(json.dumps({'revision':REV,'scope':'All syntactic imports, including deferred/optional branches; no upstream execution',
        'new_source_body_bytes':downloaded,'modules':sorted(modules,key=lambda x:x['path']),
        'third_party_import_sites':externals,'third_party_roots':sorted({x['module'].split('.')[0] for x in externals}),
        'nondeferred_unguarded_external_roots':sorted({x['module'].split('.')[0] for x in externals
            if not x['importerror_guard'] and not x['deferred_scope'] and
            (not x['main_guard'] or x['source_path']=='mtk.py')}),
        'python_stdlib_classifier_version':f'{sys.version_info.major}.{sys.version_info.minor}',
        'unresolved':unresolved,'dynamic_imports_and_runtime_paths_fully_audited':False,
        'minimal_installation_verified':False,'mac_runtime_verified':False,'tablet_accessed':False},indent=2))


if __name__=='__main__':
    main()
