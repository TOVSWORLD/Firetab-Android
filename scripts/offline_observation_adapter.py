#!/usr/bin/env python3
"""Owned adapter sequencing for injected fake backends; no native imports or CLI.

Assumes handshake/entry separately established; does not implement either.
Protocol mapping is explicit input, unqualified, and never grants readiness.
"""
from offline_observation_session import OfflineObservationSession
from offline_query_frame import validate_frame


class OfflineObservationAdapter:
    def __init__(self, backend, *, interface, commands):
        if type(interface) is not int or not 0 <= interface <= 255:
            raise ValueError('Explicit interface required')
        if type(commands) is not dict or set(commands) != {'hardware_code','hardware_versions','target_config'}:
            raise ValueError('Exact fixed query plan required')
        if any(type(v) is not bytes or len(v)!=1 for v in commands.values()) or len(set(commands.values()))!=3:
            raise ValueError('Distinct single-byte query mapping required')
        self.backend=backend;self.interface=interface;self.commands=dict(commands);self.used=False

    def collect(self):
        if self.used:raise RuntimeError('Adapter cannot be reused')
        self.used=True;claimed=False;result=None;error=None;cleanup=True
        try:
            # Backend owns endpoint validation; only an exact True is accepted.
            if self.backend.validate_active(self.interface) is not True:
                raise ValueError('Active configuration/endpoints not validated')
            if self.backend.claim(self.interface) is not True:
                raise ValueError('Interface claim not confirmed')
            claimed=True
            def query(name,timeout_ms):
                command=self.commands[name]
                # Adapter caps every actual transfer at the design budget.
                timeout=min(timeout_ms,500)
                written=self.backend.write(command,timeout_ms=timeout)
                if type(written) is not int or written!=len(command):
                    raise ValueError('Incomplete command write')
                echo=self.backend.read(1,timeout_ms=timeout)
                if type(echo) is not bytes or echo != command:
                    raise ValueError('Missing or mismatched command echo')
                payload=self.backend.read({'hardware_code':4,'hardware_versions':8,'target_config':6}[name],timeout_ms=timeout)
                return validate_frame(command=command,echo=echo,payload=payload,
                    expected_bytes={'hardware_code':4,'hardware_versions':8,'target_config':6}[name])
            # Mode exchange is not included until its deadline/framing is integrated.
            # Thus this implementation deliberately collects only the three queries.
            observation=OfflineObservationSession(query,budget_seconds=5).collect()
            result={'observation':observation,'mode_evidence':None}
        except Exception as exc:
            error=type(exc).__name__
        finally:
            if claimed:
                try:
                    if self.backend.release(self.interface) is not True:cleanup=False
                except Exception:cleanup=False
            try:
                if self.backend.dispose() is not True:cleanup=False
            except Exception:cleanup=False
        if not cleanup:result=None
        return {'accepted_offline_observation':result is not None,'result':result,
                'error_class':error,'cleanup_confirmed':cleanup,
                'protocol_mode_verified':False,'physical_test_ready':False,'bootstrap_authorized':False}
