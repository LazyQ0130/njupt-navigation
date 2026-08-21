import sys
import unittest
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon, mapping

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apply_field_review import build_updates  # noqa: E402
from gis_review import analyze_intersections, classify_endpoints  # noqa: E402


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
        self.assertEqual(buildings["osm:way:1"]["name"], "教学2号楼")
        self.assertIsNone(entrances[0]["properties"]["cyclingAccess"])


if __name__ == "__main__":
    unittest.main()
