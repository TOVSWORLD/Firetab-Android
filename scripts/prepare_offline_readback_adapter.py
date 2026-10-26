#!/usr/bin/env python3
"""Prepare ignored source-review text only; never import/execute a device helper."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
from preflight_mac_usb_library import inspect_file
from stage_libusb_static_candidate import DYLIB_SHA

ROOT=Path(__file__).resolve().parents[1]
INPUTS={'mtkclient/Library/Connection/usblib.py':'721d83047f70702413dcef76c0a63b90bfa38abf5146699b4726dceee4816986',
        'mtkclient/Library/DA/legacy/dalegacy_lib.py':'e93acdf7067a787e2e376f31c9df1328ca4757f8f8db5df212e058d5da50b86f'}


def guard_region_selection(source):
    tree=ast.parse(source)
    classes=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='DALegacy']
    methods=[n for cls in classes for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='readflash']
    if len(methods)!=1:raise ValueError('Expected one legacy read method')
    class Guard(ast.NodeTransformer):
        count=0
        def visit_Expr(self,node):
            if isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='self.sdmmc_switch_part':
                self.count+=1
                return ast.copy_location(ast.If(test=ast.Compare(left=node.value,ops=[ast.IsNot()],
                    comparators=[ast.Constant(True)]),body=[ast.Raise(exc=ast.Call(func=ast.Name(
                    id='RuntimeError',ctx=ast.Load()),args=[ast.Constant('Region selection not acknowledged; read aborted')],keywords=[]),cause=None)],orelse=[]),node)
            return node
    transformer=Guard();transformer.visit(methods[0])
    if transformer.count!=1:raise ValueError('Unexpected region-selection sites; re-audit')
    ast.fix_missing_locations(tree)
    result=ast.unparse(tree)+'\n';ast.parse(result)
    return result


def select_darwin_library(source, path):
    tree=ast.parse(source)
    if not any(isinstance(n,ast.Import) and any(x.name=='sys' for x in n.names) for n in tree.body):
        raise ValueError('Expected existing sys import')
    matches=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and ast.unparse(node.func)=='usb.backend.libusb1.get_backend':
            for keyword in node.keywords:
                value=keyword.value
                if (keyword.arg=='find_library' and isinstance(value,ast.Lambda) and
                    isinstance(value.body,ast.Constant) and value.body.value=='libusb-1.0.so'):
                    matches.append(value)
    if len(matches)!=1:raise ValueError('Expected one pinned library lookup; re-audit')
    original=matches[0].body
    matches[0].body=ast.IfExp(test=ast.Call(func=ast.Attribute(value=ast.Attribute(value=
        ast.Name(id='sys',ctx=ast.Load()),attr='platform',ctx=ast.Load()),attr='startswith',ctx=ast.Load()),
        args=[ast.Constant('darwin')],keywords=[]),body=ast.Constant(str(path)),orelse=original)
    ast.fix_missing_locations(tree)
    result=ast.unparse(tree)+'\n';ast.parse(result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();target=args.output.resolve()
    if target.exists() or not target.is_relative_to((ROOT/'out').resolve()):
        parser.error('Fresh ignored out/ subdirectory required')
    library=(ROOT/'out/libusb-artifact/libusb-1.0.0.dylib').resolve(strict=True)
    static=inspect_file(library)
    if static['sha256']!=DYLIB_SHA:raise ValueError('Pinned library identity mismatch')
    prepared=[]
    for name,digest in INPUTS.items():
        raw=(ROOT/'out/recovery-entry/mtkclient'/name).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Pinned source identity mismatch')
        source=raw.decode()
        reviewed=select_darwin_library(source,library) if name.endswith('/usblib.py') else guard_region_selection(source)
        prepared.append((name,reviewed,{'source_path':name,'original_sha256':digest,
                         'review_text_sha256':hashlib.sha256(reviewed.encode()).hexdigest()}))
    target.mkdir(parents=True)
    for name,text,_ in prepared:
        # Text extension deliberately prevents this review artifact being an importable replacement.
        destination=target/(Path(name).name+'.review.txt');destination.write_text(text)
    report={'scope':'Offline host source-review transformations only; not a runnable helper package',
        'source_revision':'7cb40e727727dfe3faa065eefb29b16ed29bbdf1',
        'library_sha256':static['sha256'],'review_texts':[record for _,_,record in prepared],
        'darwin_explicit_library_path_prepared':True,'strict_read_region_ack_guard_prepared':True,
        'upstream_helper_imported_or_executed':False,'native_code_loaded':False,'usb_enumerated':False,
        'actual_readback_verified':False,'bootstrap_effects_qualified':False,'physical_test_ready':False}
    (target/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
