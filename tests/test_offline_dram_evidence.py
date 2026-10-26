import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from offline_dram_evidence import decode, FIELDS


def fixture():
    # Entirely synthetic fields; this is not a device transcript.
    return dict(version_reply=b'A', requested_length=(188).to_bytes(4,'big'),
                checksum=b'xx', status=bytes(4), ram_type=b'R', chip_select=b'C',
                ram_bytes=(1024).to_bytes(8,'big'))


class DramEvidenceTests(unittest.TestCase):
    def test_complete_synthetic_fields_never_authorize_stage_or_geometry(self):
        result=decode(fixture(),expected_ack=b'A',local_emi_bytes=188)
        self.assertEqual(result['agent_reported_ram_bytes'],1024)
        for key in ['checksum_integrity_verified','response_provenance_verified',
                    'dram_capacity_or_layout_verified','stage_transfer_authorized','physical_test_ready']:
            self.assertFalse(result[key])

    def test_every_short_or_oversized_field_rejected(self):
        for name in FIELDS:
            for replacement in [fixture()[name][:-1],fixture()[name]+b'x',None]:
                fields=fixture();fields[name]=replacement
                with self.assertRaises(ValueError):decode(fields,expected_ack=b'A',local_emi_bytes=188)

    def test_unknown_reply_length_status_and_zero_size_rejected(self):
        for key,value in [('version_reply',b'?'),('requested_length',(189).to_bytes(4,'big')),
                          ('status',(1).to_bytes(4,'big')),('ram_bytes',bytes(8))]:
            fields=fixture();fields[key]=value
            with self.assertRaises(ValueError):decode(fields,expected_ack=b'A',local_emi_bytes=188)
        with self.assertRaises(ValueError):decode({},expected_ack=b'A',local_emi_bytes=188)
        with self.assertRaises(ValueError):decode(fixture(),expected_ack=True,local_emi_bytes=188)
