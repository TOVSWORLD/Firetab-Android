"""Release gate behavior with temporary fixtures, never product evidence."""
import copy
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import check_release as release
from ci import STAGES


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.write('releases/policy.json', json.loads((release.ROOT / 'releases/policy.json').read_text()))
        (self.root / 'notes.md').write_text('Test-only notes; no firmware.\n')
        self.snapshot = dict(project='workspace', version='0.1.0', tag='workspace-v0.1.0', kind='source-snapshot', tested_revision='a'*40, notes='notes.md', native_runtime=False, artifacts=[])

    def write(self, path, obj):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(obj))

    def firmware(self):
        data = dict(self.snapshot, project='firetabs-android', kind='firmware', version='0.1.0-alpha.1', tag='firetabs-android-v0.1.0-alpha.1')
        data['artifacts'] = [dict(path='image.img', bytes=4, sha256=hashlib.sha256(b'test').hexdigest())]
        data['provenance'] = dict(source_manifest='notes.md', toolchain='notes.md', device_matrix='notes.md')
        log = self.root / 'test.log'
        log.write_text('Test fixture only.\n')
        evidence = [dict(path='test.log', sha256=hashlib.sha256(log.read_bytes()).hexdigest())]
        stages = {name: dict(status='passed', revision='a'*40, evidence=copy.deepcopy(evidence)) for name in STAGES['firetabs-android']}
        self.write('projects/firetabs-android/validation.json', dict(project='firetabs-android', stages=stages))
        return data

    def test_workspace_snapshot_accepts_no_runtime_claim(self):
        release.validate_manifest(self.snapshot, self.root)

    def test_workspace_cannot_hide_runtime_assets(self):
        with self.assertRaisesRegex(ValueError, 'cannot distribute'):
            release.validate_manifest(dict(self.snapshot, artifacts=[{'path':'image.img'}]), self.root)

    def test_wrong_prefix_and_invalid_versions(self):
        for version in ['01.2.3', '1.0', '1.0.0-latest', '1.0.0-alpha.0']:
            with self.assertRaises(ValueError):
                release.validate_manifest(dict(self.snapshot, version=version), self.root)
        with self.assertRaisesRegex(ValueError, 'prefix mismatch'):
            release.validate_manifest(dict(self.snapshot, tag='firetabs-android-v0.1.0'), self.root)

    def test_unbooted_firmware_rejected(self):
        data = self.firmware()
        progress = json.loads((self.root/'projects/firetabs-android/validation.json').read_text())
        for name in ['boot','hardware','general_purpose_soak']:
            progress['stages'][name] = dict(status='not_run', revision=None, evidence=[])
        self.write('projects/firetabs-android/validation.json', progress)
        with self.assertRaisesRegex(ValueError, 'Unpassed release gate: boot'):
            release.validate_manifest(data, self.root)

    def test_old_revision_is_not_candidate_evidence(self):
        data = self.firmware()
        data['tested_revision'] = 'b'*40
        with self.assertRaisesRegex(ValueError, 'Stale evidence'):
            release.validate_manifest(data, self.root)

    def test_stable_requires_support_record(self):
        data = self.firmware()
        data.update(version='1.0.0', tag='firetabs-android-v1.0.0', support_record='support.json')
        with self.assertRaisesRegex(ValueError, 'Missing/empty record'):
            release.validate_manifest(data, self.root)
        self.write('support.json', dict(project='firetabs-android',version='1.0.0',maintainer='Test fixture',starts=date.today().isoformat(),ends=(date.today()+timedelta(days=365)).isoformat(),install='notes.md',upgrade='notes.md',recovery='notes.md'))
        release.validate_manifest(data, self.root)

    def test_local_artifact_content_and_escape(self):
        data = self.firmware()
        (self.root/'image.img').write_bytes(b'test')
        release.validate_manifest(data, self.root, self.root)
        (self.root/'image.img').write_bytes(b'fail')
        with self.assertRaisesRegex(ValueError, 'content mismatch'):
            release.validate_manifest(data, self.root, self.root)
        data['artifacts'][0]['path'] = '../escape'
        with self.assertRaisesRegex(ValueError, 'Unsafe path'):
            release.validate_manifest(data, self.root, self.root)


if __name__ == '__main__':
    unittest.main()
