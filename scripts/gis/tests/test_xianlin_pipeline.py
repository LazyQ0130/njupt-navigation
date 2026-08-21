import sys
import unittest
from pathlib import Path

from shapely.geometry import Point, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from xianlin_pipeline import (  # noqa: E402
    apply_override,
    apply_aliases,
    building_category,
    feature,
    height_properties,
    stable_id,
    validate,
    way_polygon,
)


class XianlinPipelineTest(unittest.TestCase):
    def test_stable_osm_id(self):
        self.assertEqual(stable_id({"type": "way", "id": 123}), "osm:way:123")
        self.assertEqual(stable_id({"type": "way", "id": 123}, "poi"), "osm:way:123:poi")

    def test_osm_mapping_and_level_height(self):
        element = {"type": "way", "id": 1, "tags": {"name": "学生宿舍", "building": "dormitory", "building:levels": "6"}}
        self.assertEqual(building_category(element), "DORMITORY")
        self.assertEqual(height_properties(element), {"height": 19.8, "heightSource": "ESTIMATED_FROM_LEVELS"})

    def test_rejects_open_polygon(self):
        element = {"type": "way", "id": 1, "geometry": [{"lon": 118.9, "lat": 32.1}, {"lon": 118.91, "lat": 32.1}, {"lon": 118.91, "lat": 32.11}]}
        self.assertIsNone(way_polygon(element))

    def test_manual_override_keeps_stable_id(self):
        item = feature(Polygon([(0, 0), (1, 0), (1, 1), (0, 0)]), {"externalId": "osm:way:7", "name": "旧名称"})
        updated = apply_override(item, {"osm:way:7": {"name": "已核验名称", "verificationStatus": "MANUALLY_REVIEWED"}})
        self.assertEqual(updated["properties"]["externalId"], "osm:way:7")
        self.assertEqual(updated["properties"]["name"], "已核验名称")

    def test_confirmed_aliases_apply_by_exact_name(self):
        item = feature(Point(118.92, 32.11), {"externalId": "manual:test", "name": "教学2号楼", "aliases": []})

        updated = apply_aliases(item, {"教学2号楼": ["教2", "教二"]})

        self.assertEqual(updated["properties"]["aliases"], ["教2", "教二"])

    def test_coordinate_validation_rejects_non_wgs84_range(self):
        campus = feature(
            Polygon([(118.92, 32.11), (118.93, 32.11), (118.93, 32.12), (118.92, 32.11)]),
            {"externalId": "osm:way:1", "name": "校界", "featureType": "CAMPUS_BOUNDARY"},
        )
        bad_poi = feature(
            Point(218.92, 32.11),
            {"externalId": "osm:node:2", "name": "错误坐标", "featureType": "POI"},
        )
        layers = {"campus": [campus], "buildings": [], "roads": [], "surfaces": [], "pois": [bad_poi], "entrances": []}

        report = validate(layers, {})

        self.assertEqual(report["error"], 2)
        self.assertEqual(report["coordinateErrors"][0]["id"], "osm:node:2")


if __name__ == "__main__":
    unittest.main()
