import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_observation_session import OfflineObservationSession


class ObservationSessionTests(unittest.TestCase):
    def test_exact_symbolic_queries_and_no_bootstrap_authorization(self):
        calls=[]
        def query(name,timeout_ms):
            calls.append((name,timeout_ms))
            return bytes({'hardware_code':4,'hardware_versions':8,'target_config':6}[name])
        session=OfflineObservationSession(query)
        result=session.collect()
        self.assertEqual([x[0] for x in calls],['hardware_code','hardware_versions','target_config'])
        self.assertTrue(all(0 < x[1] <= 1000 for x in calls))
        self.assertFalse(result['bootstrap_authorized'])
        self.assertFalse(result['protocol_mode_verified'])
        with self.assertRaises(RuntimeError):session.collect()

    def test_every_short_query_aborts_without_retry_or_fallback(self):
        names=['hardware_code','hardware_versions','target_config']
        for failure in names:
            calls=[]
            def query(name,timeout_ms):
                calls.append(name)
                return b'' if name == failure else bytes({'hardware_code':4,'hardware_versions':8,'target_config':6}[name])
            session=OfflineObservationSession(query)
            with self.assertRaises(ValueError):session.collect()
            self.assertEqual(calls,names[:names.index(failure)+1])
            self.assertEqual(session.state,'invalid')
            with self.assertRaises(RuntimeError):session.collect()

    def test_late_callback_invalidates_session(self):
        now=[0.0]
        def query(name,timeout_ms):
            now[0]+=2
            return bytes(4)
        session=OfflineObservationSession(query,budget_seconds=1,clock=lambda:now[0])
        with self.assertRaises(TimeoutError):session.collect()
        self.assertEqual(session.state,'invalid')

    def test_nonzero_version_status_is_rejected(self):
        def query(name,timeout_ms):
            return bytes(6)+b'\x00\x01' if name=='hardware_versions' else bytes({'hardware_code':4,'target_config':6}[name])
        with self.assertRaises(ValueError):OfflineObservationSession(query).collect()
