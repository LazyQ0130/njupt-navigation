import sys
import unittest
from pathlib import Path

from shapely.geometry import Point, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from xianlin_pipeline import (  # noqa: E402
    apply_override,
    apply_aliases,
    apply_review,
    apply_naming_semantics,
    building_category,
    feature,
    height_properties,
    dormitory_candidate,
    dormitory_zone_for_number,
    generate_dormitory_zones,
    stable_id,
    validate,
    way_polygon,
)
from naming_audit import _duplicate_groups  # noqa: E402


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

    def test_manual_review_changes_status_without_changing_source_lineage(self):
        item = feature(Point(118.92, 32.11), {
            "externalId": "osm:node:1", "name": "地点", "dataSource": "OPENSTREETMAP",
            "verificationStatus": "SOURCE_VERIFIED",
        })

        updated = apply_review(item, {"osm:node:1": {
            "status": "MANUALLY_REVIEWED", "reviewedAt": "2026-08-22",
            "reviewMethod": "OFFICIAL_REFERENCE", "nameVerified": True,
            "geometryVerified": False, "reviewedBy": "manual-review", "notes": "官方地图核对",
        }})

        self.assertEqual(updated["properties"]["verificationStatus"], "MANUALLY_REVIEWED")
        self.assertEqual(updated["properties"]["dataSource"], "OPENSTREETMAP")

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

    def test_explicit_dormitory_number_gets_separate_zone_and_building_semantics(self):
        candidate = dormitory_candidate("25", "DORMITORY")

        self.assertEqual(candidate["number"], "25")
        self.assertEqual(candidate["displayName"], "25号楼")
        self.assertEqual(candidate["confidence"], "HIGH")

        item = feature(Point(118.92, 32.11), {
            "externalId": "osm:way:25", "name": "25", "featureType": "BUILDING",
            "category": "DORMITORY", "aliases": [],
        })
        apply_naming_semantics(item)
        self.assertEqual(item["properties"]["displayName"], "25号楼")
        self.assertEqual(item["properties"]["officialName"], "25号学生宿舍")
        self.assertEqual(item["properties"]["buildingNumber"], "25")
        self.assertEqual(item["properties"]["dormitoryZone"], "桃苑")
        self.assertIn("桃苑25号楼", item["properties"]["aliases"])
        self.assertTrue(item["properties"]["labelVisible"])

    def test_zone_mapping_uses_the_source_transcription(self):
        expected = {
            "1": "梅苑", "6": "梅苑", "7": "兰苑", "12": "兰苑",
            "13": "竹苑", "15": "竹苑", "16": "菊苑", "21": "菊苑",
            "22": "桃苑", "27": "桃苑", "28": "李苑", "33": "李苑",
            "34": "柳苑", "39": "柳苑", "40": "桂苑", "45": "桂苑",
            "46": "南荷", "47": "南荷", "48": "北荷", "49": "北荷",
        }
        self.assertEqual({number: dormitory_zone_for_number(number) for number in expected}, expected)
        self.assertIsNone(dormitory_zone_for_number("50"))

    def test_dormitory_zone_label_points_are_deterministic_unique_and_traceable(self):
        def dormitory(number, x):
            item = feature(
                Polygon([(x, 32.11), (x + 0.0001, 32.11), (x + 0.0001, 32.1101), (x, 32.11)]),
                {
                    "externalId": f"osm:way:{number}", "name": number,
                    "featureType": "BUILDING", "category": "DORMITORY", "aliases": [],
                },
            )
            return apply_naming_semantics(item)

        buildings = [dormitory("34", 118.92), dormitory("35", 118.921)]

        first = generate_dormitory_zones(buildings)
        second = generate_dormitory_zones(buildings)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["properties"]["name"], "柳苑")
        self.assertEqual(first[0]["properties"]["geometryRole"], "LABEL_ONLY")
        self.assertEqual(first[0]["properties"]["verificationStatus"], "SOURCE_VERIFIED")
        self.assertTrue(first[0]["properties"]["sourceUrl"])
        self.assertEqual(first[0]["geometry"]["type"], "Point")

    def test_generic_and_long_institution_building_labels_are_suppressed(self):
        generic = feature(Point(0, 0), {
            "externalId": "generic", "name": "教学楼", "featureType": "BUILDING", "category": "TEACHING",
        })
        institution = feature(Point(0, 0), {
            "externalId": "college", "name": "计算机学院", "featureType": "BUILDING", "category": "TEACHING",
        })
        department = feature(Point(0, 0), {
            "externalId": "department", "name": "工程实验教学部", "featureType": "BUILDING", "category": "TEACHING",
        })

        self.assertFalse(apply_naming_semantics(generic)["properties"]["labelVisible"])
        self.assertFalse(apply_naming_semantics(institution)["properties"]["labelVisible"])
        self.assertFalse(apply_naming_semantics(department)["properties"]["labelVisible"])

    def test_duplicate_naming_groups_keep_all_physical_ids(self):
        buildings = [
            {"properties": {"externalId": "building-a", "name": "一食堂"}},
            {"properties": {"externalId": "building-b", "name": "一食堂"}},
            {"properties": {"externalId": "building-c", "name": "图书馆"}},
        ]

        self.assertEqual(_duplicate_groups(buildings), {
            "一食堂": ["building-a", "building-b"],
        })


if __name__ == "__main__":
    unittest.main()
