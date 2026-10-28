import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_clock_references import hdmi_policy, UNQUALIFIED_HDMI


class HdmiConsumerPolicy(unittest.TestCase):
    def test_real_audio_divider_and_dsi_are_not_conflated_with_hdmi_aliases(self):
        r = hdmi_policy([{'symbol': s} for s in
                         ['CLK_AUDIO_APLL2_DIV0', 'CLK_MM_DSI_ENGINE', 'CLK_MM_DSI_DIGITAL']])
        self.assertEqual(r['captured_restricted_consumers'], [])

    def test_each_unresolved_dependent_branch_is_rejected(self):
        for symbol in UNQUALIFIED_HDMI:
            with self.subTest(symbol=symbol), self.assertRaisesRegex(ValueError, '#29'):
                hdmi_policy([{'symbol': 'CLK_MM_DSI_ENGINE'}, {'symbol': symbol}])

    def test_mixed_and_duplicate_forbidden_inputs_cannot_mask_the_dependency(self):
        with self.assertRaisesRegex(ValueError, 'CLK_MM_HDMI_SPDIF'):
            hdmi_policy([{'symbol': 'CLK_AUDIO_APLL2_DIV0'},
                         {'symbol': 'CLK_MM_HDMI_SPDIF'}, {'symbol': 'CLK_MM_HDMI_SPDIF'}])
