import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from shapely.geometry import LineString, Point, Polygon, mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apply_field_review import build_dormitory_updates, build_updates  # noqa: E402
from gis_review import analyze_intersections, classify_endpoints, entrance_validation  # noqa: E402
from xianlin_pipeline import apply_override, apply_review, apply_road_overrides  # noqa: E402


def item(geometry, external_id, feature_type, name, category="OTHER", **properties):
    return {
        "type": "Feature",
        "geometry": mapping(geometry),
        "properties": {
            "externalId": external_id,
            "featureType": feature_type,
            "name": name,
            "category": category,
            "verificationStatus": "SOURCE_VERIFIED",
            **properties,
        },
    }


class GisReviewTest(unittest.TestCase):
    def layers(self):
        return {
            "campus": [item(Polygon([(0, 0), (100, 0), (100, 100), (0, 100), (0, 0)]), "campus", "CAMPUS_BOUNDARY", "Campus")],
            "roads": [
                item(LineString([(10, 10), (20, 10)]), "road-a", "ROAD_MAIN", "Main A"),
                item(LineString([(21, 10), (30, 10)]), "road-b", "ROAD_MAIN", "Main B"),
                item(LineString([(45, 50), (50, 50)]), "path-c", "ROAD_PEDESTRIAN", "Path C"),
                item(LineString([(10, 80), (0.5, 80)]), "path-d", "ROAD_PEDESTRIAN", "Boundary Path"),
            ],
            "buildings": [item(Polygon([(51.5, 48), (60, 48), (60, 55), (51.5, 55), (51.5, 48)]), "building-1", "BUILDING", "Building")],
            "surfaces": [],
            "pois": [],
            "entrances": [],
        }

    def test_endpoint_classification_nearest_road_building_boundary_and_candidates(self):
        features, report, candidates = classify_endpoints(self.layers(), lambda geometry: geometry)
        classifications = {feature["properties"]["classification"] for feature in features}

        self.assertIn("LIKELY_TOPOLOGY_GAP", classifications)
        self.assertIn("NEAR_BUILDING_ENTRANCE", classifications)
        self.assertIn("NEAR_CAMPUS_BOUNDARY", classifications)
        gap = next(feature for feature in features if feature["properties"]["classification"] == "LIKELY_TOPOLOGY_GAP")
        self.assertEqual(gap["properties"]["distanceMeters"], 1.0)
        self.assertFalse(gap["properties"]["suggestedFix"]["applied"])
        self.assertGreaterEqual(report["candidateEntranceCount"], 1)
        self.assertEqual(candidates[0]["properties"]["buildingId"], "building-1")

    def test_intersection_report_preserves_geometry_and_cause(self):
        layers = self.layers()
        layers["roads"].append(item(LineString([(52, 49), (59, 49)]), "road-cross", "ROAD_MAIN", "Crossing"))

        intersections = analyze_intersections(layers, lambda geometry: geometry)

        crossing = next(feature for feature in intersections if feature["properties"]["roadId"] == "road-cross")
        self.assertGreater(crossing["properties"]["intersectionLengthMeters"], 1)
        self.assertEqual(crossing["properties"]["likelyCause"], "A_OR_B_REQUIRES_MANUAL_REVIEW")

    def test_field_review_builds_traceable_manual_updates(self):
        rows = [{
            "object_id": "osm:way:1", "object_type": "BUILDING", "current_name": "教2",
            "confirmed_name": "教学2号楼", "status": "FIELD_VERIFIED", "entrance_lat": "32.11",
            "entrance_lon": "118.92", "walking_access": "true", "cycling_access": "",
            "accessible": "false", "notes": "现场确认",
        }]

        reviews, buildings, _, entrances = build_updates(rows, "2026-08-22", "manual-review")

        self.assertEqual(reviews[0]["status"], "FIELD_VERIFIED")
        self.assertEqual(reviews[0]["reviewMethod"], "FIELD_CHECK")
        self.assertTrue(reviews[0]["nameVerified"])
        self.assertFalse(reviews[0]["geometryVerified"])
        self.assertEqual(buildings["osm:way:1"]["name"], "教学2号楼")
        self.assertEqual(buildings["osm:way:1"]["officialName"], "教学2号楼")
        self.assertIsNone(entrances[0]["properties"]["cyclingAccess"])
        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[1]["objectId"], entrances[0]["properties"]["externalId"])
        self.assertTrue(reviews[1]["geometryVerified"])

    def test_review_manifest_has_final_status_precedence_and_dimensions(self):
        feature = item(Point(1, 1), "osm:way:1", "BUILDING", "教1")
        feature["properties"]["verificationStatus"] = "MANUALLY_REVIEWED"
        reviews = {"osm:way:1": {
            "objectId": "osm:way:1", "status": "FIELD_VERIFIED",
            "reviewedAt": "2026-08-22", "reviewMethod": "FIELD_CHECK",
            "nameVerified": True, "geometryVerified": False, "notes": "名称现场确认",
        }}

        apply_review(feature, reviews)

        self.assertEqual(feature["properties"]["verificationStatus"], "FIELD_VERIFIED")
        self.assertEqual(feature["properties"]["reviewMethod"], "FIELD_CHECK")
        self.assertTrue(feature["properties"]["nameVerified"])
        self.assertFalse(feature["properties"]["geometryVerified"])

    def test_confirmed_dormitory_requires_explicit_review_and_builds_safe_names(self):
        rows = [{
            "osm_id": "osm:way:25", "confirmed_number": "25",
            "confirmed_display_name": "25号楼", "aliases": "25栋|25号学生公寓",
            "status": "MANUALLY_REVIEWED", "notes": "用户对照校园资料确认",
        }]

        reviews, buildings = build_dormitory_updates(rows, "2026-08-22")

        self.assertEqual(reviews[0]["reviewMethod"], "USER_MANUAL_REVIEW")
        self.assertEqual(buildings["osm:way:25"]["officialName"], "25号学生宿舍")
        self.assertEqual(buildings["osm:way:25"]["displayName"], "25号楼")
        self.assertIn("25号宿舍", buildings["osm:way:25"]["aliases"])

    def test_manual_override_survives_changed_osm_name_and_keeps_stable_id(self):
        override = {"osm:way:1": {
            "officialName": "教学1号楼", "displayName": "教1",
            "verificationStatus": "MANUALLY_REVIEWED",
        }}
        first = item(Point(1, 1), "osm:way:1", "BUILDING", "旧 OSM 名称")
        refreshed = item(Point(1, 1), "osm:way:1", "BUILDING", "刷新后的 OSM 名称")

        apply_override(first, override)
        apply_override(refreshed, override)

        self.assertEqual(refreshed["properties"]["externalId"], "osm:way:1")
        self.assertEqual(refreshed["properties"]["displayName"], "教1")
        self.assertEqual(refreshed["properties"]["verificationStatus"], "MANUALLY_REVIEWED")

    def test_confirmed_merge_endpoint_override_is_traceable_and_minimal(self):
        road = item(LineString([(0, 0), (1, 0)]), "road-a", "ROAD_MAIN", "Road A")
        override = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": mapping(LineString([(0, 0), (1.1, 0)])),
                "properties": {
                    "operation": "MERGE_ENDPOINT", "sourceObjectId": "road-a",
                    "verificationStatus": "FIELD_VERIFIED", "reviewedAt": "2026-08-22",
                    "reviewedBy": "manual-review", "reason": "现场确认连通",
                },
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "road-overrides.geojson"
            path.write_text(json.dumps(override), encoding="utf-8")
            with patch("xianlin_pipeline.MANUAL_DIR", Path(directory)):
                updated = apply_road_overrides([road])

        self.assertEqual(updated[0]["properties"]["externalId"], "road-a")
        self.assertEqual(updated[0]["properties"]["manualOperation"], "MERGE_ENDPOINT")
        self.assertEqual(updated[0]["geometry"]["coordinates"][-1], [1.1, 0.0])

    def test_formal_entrance_validation_checks_building_and_network_distance(self):
        layers = self.layers()
        layers["entrances"] = [item(
            Point(51.5, 50), "entrance-1", "ENTRANCE", "主要入口",
            buildingExternalId="building-1",
        )]

        result = entrance_validation(layers, lambda geometry: geometry)

        self.assertEqual(result[0]["boundaryStatus"], "OK")
        self.assertEqual(result[0]["networkStatus"], "OK")


if __name__ == "__main__":
    unittest.main()
