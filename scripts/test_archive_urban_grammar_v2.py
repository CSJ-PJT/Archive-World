import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "config" / "archive-urban-grammar-v2.json"


class ArchiveUrbanGrammarV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_reference_chain_and_originality_boundary(self):
        policy = self.data["referencePolicy"]
        self.assertTrue(policy["abstractPrinciplesOnly"])
        self.assertFalse(policy["directReproductionAllowed"])
        self.assertEqual(
            policy["transformationChain"],
            [
                "reference-evidence",
                "urban-principle",
                "archive-grammar",
                "archive-native-geometry",
                "archive-scene-evidence",
            ],
        )

    def test_street_camera_is_near_field_first(self):
        camera = self.data["sceneGates"]["streetCamera"]
        self.assertLessEqual(camera["maxBlankPavementRatio"], 0.15)
        self.assertLessEqual(camera["maxForegroundObstructionRatio"], 0.12)
        self.assertGreaterEqual(camera["minDepthLayers"], 4)
        self.assertTrue(camera["requiresActiveFrontage"])
        self.assertTrue(camera["requiresVisibleEntrance"])

    def test_windows_are_part_of_a_closed_envelope(self):
        building = self.data["building"]
        self.assertEqual(building["detachedWindowCount"], 0)
        self.assertTrue(building["requiresWallReturns"])
        self.assertTrue(building["requiresRoomBackShadow"])
        self.assertLess(building["windowRecessM"][0], building["windowRecessM"][1])

    def test_frontage_targets_are_not_diluted(self):
        targets = self.data["frontage"]["targets"]
        self.assertGreaterEqual(targets["archive-water-plaza"], 0.80)
        self.assertGreaterEqual(targets["ledger-stream-terrace"], 0.75)
        self.assertGreaterEqual(targets["transit-stream-junction"], 0.75)
        self.assertGreaterEqual(len(self.data["frontage"]["requiredInteriorLayers"]), 8)

    def test_stream_is_a_multilevel_continuous_section(self):
        stream = self.data["stream"]
        self.assertGreater(stream["upperToLowerLevelDifferenceM"][0], 0)
        self.assertLessEqual(stream["maxIdenticalEdgeRunM"], 50)
        self.assertIn("accessible", stream["requiredContinuities"])
        self.assertIn("fire-service", stream["requiredContinuities"])

    def test_night_is_selective_not_uniform(self):
        night = self.data["night"]
        self.assertFalse(night["allWindowsEmissiveAllowed"])
        self.assertFalse(night["waterSurfaceEmissiveAllowed"])
        self.assertLessEqual(night["towerWindowOccupancyRatio"][1], 0.35)

    def test_performance_and_protection_gates(self):
        performance = self.data["sceneGates"]["performance"]
        self.assertLess(performance["hardMaxDrawCalls"], 400)
        self.assertGreaterEqual(performance["targetAverageFps"], 30)
        self.assertGreaterEqual(performance["targetOnePercentLowFps"], 20)
        self.assertTrue(all(value is False for value in self.data["protection"].values()))


if __name__ == "__main__":
    unittest.main()
