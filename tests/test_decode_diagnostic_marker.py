import hashlib
import unittest
from decode_diagnostic_marker import decode_marker, LAYOUTS, MARKER


class MarkerTests(unittest.TestCase):
    def data(self, variant='callable'):
        marker, stack, total = LAYOUTS[variant]
        image = bytes([0x55]) * marker + bytes(stack - marker) + bytes(total - stack)
        return image, hashlib.sha256(image).hexdigest()

    def decode(self, image, after, variant='callable', digest=None, before=None):
        return decode_marker(image, image if before is None else before, after,
                             variant=variant, expected_image_sha256=digest or hashlib.sha256(image).hexdigest())

    def test_transition_and_stack_changes_are_not_runtime_proof(self):
        for variant in LAYOUTS:
            image, digest = self.data(variant); offset, stack, _ = LAYOUTS[variant]
            after = bytearray(image); after[offset:offset+4] = MARKER; after[stack] = 1
            result = self.decode(image, bytes(after), variant, digest)
            self.assertTrue(result['supplied_marker_transition'])
            self.assertEqual(result['stack_bytes_changed'], 1)
            self.assertFalse(result['runtime_execution_verified'])
            self.assertFalse(result['caller_return_verified'])

    def test_unchanged_snapshot_is_not_transition(self):
        image, _ = self.data()
        self.assertFalse(self.decode(image, image)['supplied_marker_transition'])

    def test_rejects_identity_stale_before_and_code_change(self):
        image, _ = self.data()
        changed = bytearray(image); changed[0] ^= 1
        for after, kwargs in [(image, {'digest':'0'*64}), (image, {'before':bytes(changed)}), (bytes(changed), {})]:
            with self.assertRaises(ValueError): self.decode(image, after, **kwargs)

    def test_rejects_wrong_size_type_marker_and_variant(self):
        image, _ = self.data(); bad = bytearray(image); bad[48:52] = b'bad!'
        for after, kwargs in [(image[:-1], {}), (bytearray(image), {}), (bytes(bad), {}), (image, {'variant':'unknown'})]:
            with self.assertRaises(ValueError): self.decode(image, after, **kwargs)
