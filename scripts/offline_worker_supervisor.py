#!/usr/bin/env python3
"""Spawned trusted-worker deadline contract. No device/helper binding or CLI."""
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
import math
import multiprocessing
import os
from pathlib import Path
import shutil
import tempfile
import time


@dataclass
class WorkerOutcome:
    summary: dict
    quarantine_directory: Path | None=field(default=None,repr=False)


def _entry(worker, directory, channel):
    # This prototype intentionally has no live helper binding/log capture. Do
    # not let a fixture/worker exception dump potentially private data to CI.
    with open(os.devnull,'w') as sink,redirect_stdout(sink),redirect_stderr(sink):
        os.dup2(sink.fileno(),1);os.dup2(sink.fileno(),2)
        try:
            worker(Path(directory));channel.send_bytes(b'complete')
        except BaseException:
            try:channel.send_bytes(b'failed')
            except (OSError,EOFError):
                channel.close()
        finally:channel.close()


def supervise_worker(worker, validator, quarantine_root, *, timeout_seconds):
    if (type(timeout_seconds) not in (int,float) or not math.isfinite(timeout_seconds)
        or not 0<timeout_seconds<=30):
        raise ValueError('Explicit host-worker deadline at most30 seconds required')
    root=Path(quarantine_root)
    if not root.is_dir():raise ValueError('Existing trusted quarantine root required')
    directory=Path(tempfile.mkdtemp(prefix='.worker-unaccepted-',dir=root))
    context=multiprocessing.get_context('spawn');receive,send=context.Pipe(duplex=False)
    process=context.Process(target=_entry,args=(worker,str(directory),send),daemon=True)
    began=time.monotonic();started=False;keep=False
    summary={'worker_completed':False,'parent_validation_passed':False,'timed_out':False,
             'terminate_requested':False,'kill_requested':False,'worker_reaped':False,
             'output_published':False,'device_recovery_verified':False,'physical_test_ready':False}
    try:
        process.start();started=True;send.close()
        process.join(max(0,timeout_seconds-(time.monotonic()-began)))
        summary['timed_out']=process.is_alive() or time.monotonic()-began>timeout_seconds
        if process.is_alive():
            summary['terminate_requested']=True;process.terminate();process.join(0.25)
        if process.is_alive():
            summary['kill_requested']=True;process.kill();process.join(0.25)
        summary['worker_reaped']=not process.is_alive()
        if not summary['worker_reaped']:
            keep=True;summary['failure']='worker_not_reaped'
        elif summary['timed_out']:
            summary['failure']='worker_deadline'
        else:
            try:message=receive.recv_bytes(32) if receive.poll() else b''
            except (OSError,EOFError):message=b''
            summary['worker_completed']=process.exitcode==0 and message==b'complete'
            if not summary['worker_completed']:summary['failure']='worker_failed_or_no_completion'
            else:
                try:summary['parent_validation_passed']=validator(directory) is True
                except BaseException:summary['parent_validation_passed']=False
                if summary['parent_validation_passed']:keep=True
                else:summary['failure']='parent_validation_failed'
        # Even successful bytes remain quarantined: this function never publishes
        # a backup or marks device state safe. The caller owns further validation.
        return WorkerOutcome(summary,directory if keep else None)
    finally:
        send.close();receive.close()
        if started and process.is_alive():
            process.kill();process.join(0.25)
            keep=process.is_alive() or keep
        if not keep:shutil.rmtree(directory)
        summary['elapsed_seconds']=round(time.monotonic()-began,3)
        if started and not process.is_alive():process.close()
