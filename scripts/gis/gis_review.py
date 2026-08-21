"""Generate conservative topology and field-review artifacts for Xianlin GIS."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from shapely.geometry import LineString, Point, mapping, shape
from shapely.ops import nearest_points

EXACT_TOPOLOGY_M = 0.15
GAP_THRESHOLD_M = 2.0
NEAR_ROAD_THRESHOLD_M = 4.0
BUILDING_THRESHOLD_M = 5.0
CANDIDATE_ENTRANCE_THRESHOLD_M = 2.0
BOUNDARY_THRESHOLD_M = 10.0


def local_point(point: Point, longitude: float, latitude: float) -> Point:
    cos_lat = math.cos(math.radians(latitude))
    return Point((point.x - longitude) * 111_320 * cos_lat, (point.y - latitude) * 110_540)


def wgs84_point(point: Point, longitude: float, latitude: float) -> Point:
    cos_lat = math.cos(math.radians(latitude))
    return Point(point.x / (111_320 * cos_lat) + longitude, point.y / 110_540 + latitude)


def feature_collection(name: str, features: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "name": name,
        "metadata": {
            "generatedAt": date.today().isoformat(),
            "purpose": "MANUAL_REVIEW_ONLY",
            "appliesChanges": False,
        },
        "features": features,
    }


def review_feature(geometry, review_id: str, severity: str, reason: str,
                   source_id: str, name: str, **extra: Any) -> dict[str, Any]:
    properties = {
        "reviewId": review_id,
        "severity": severity,
        "reason": reason,
        "sourceObjectId": source_id,
        "name": name,
        "verificationStatus": "PENDING_REVIEW",
        "notes": "",
    }
    properties.update(extra)
    return {"type": "Feature", "id": review_id, "geometry": mapping(geometry), "properties": properties}


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while value != self.parent[value]:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def road_parts(geometry) -> list[LineString]:
    return list(geometry.geoms) if geometry.geom_type == "MultiLineString" else [geometry]


def core_building(name: str, category: str) -> bool:
    exact = {"教1", "教2", "教3", "教4", "教5", "图书馆", "圆楼", "青春剧场", "大学生活动中心", "新体育馆"}
    return name in exact or category in {"DINING", "ADMINISTRATION"}


def core_poi(name: str, category: str) -> bool:
    return category in {"LIBRARY", "TEACHING", "ADMINISTRATION", "SPORT"} or "食堂" in name or "快递" in name


def _nearest(point: Point, candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, float, Point | None]:
    nearest = None
    distance = math.inf
    nearest_position = None
    for candidate in candidates:
        candidate_distance = point.distance(candidate["metric"])
        if candidate_distance < distance:
            nearest = candidate
            distance = candidate_distance
            nearest_position = nearest_points(point, candidate["metric"])[1]
    return nearest, distance, nearest_position


def _snap_is_safe(segment: LineString, buildings: list[dict[str, Any]], waters: list[dict[str, Any]]) -> bool:
    for obstacle in buildings + waters:
        intersection = segment.intersection(obstacle["metric"])
        if not intersection.is_empty and getattr(intersection, "length", 0.0) > 0.25:
            return False
    return segment.is_valid and segment.is_simple


def classify_endpoints(layers: dict[str, list[dict[str, Any]]], metric) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    roads = []
    active_roads = [item for item in layers["roads"] if item["properties"].get("enabled", True)]
    for index, item in enumerate(active_roads):
        geometry = shape(item["geometry"])
        roads.append({"index": index, "feature": item, "geometry": geometry, "metric": metric(geometry)})
    buildings = [
        {"feature": item, "geometry": shape(item["geometry"]), "metric": metric(shape(item["geometry"]))}
        for item in layers["buildings"]
    ]
    waters = [
        {"feature": item, "geometry": shape(item["geometry"]), "metric": metric(shape(item["geometry"]))}
        for item in layers["surfaces"] if item["properties"]["featureType"] == "WATER"
    ]
    campus = shape(layers["campus"][0]["geometry"])
    campus_boundary = metric(campus.boundary)
    center = campus.centroid

    endpoints = []
    union = UnionFind(len(roads))
    for road in roads:
        for part_index, part in enumerate(road_parts(road["geometry"])):
            for side, coordinate in (("start", part.coords[0]), ("end", part.coords[-1])):
                point = Point(coordinate)
                endpoints.append({
                    "endpointId": f"{road['feature']['properties']['externalId']}:{part_index}:{side}",
                    "road": road,
                    "point": point,
                    "metric": metric(point),
                    "side": side,
                })

    for endpoint in endpoints:
        road_index = endpoint["road"]["index"]
        for other in roads:
            if other["index"] == road_index:
                continue
            if endpoint["metric"].distance(other["metric"]) <= EXACT_TOPOLOGY_M:
                union.union(road_index, other["index"])

    component_sizes = Counter(union.find(road["index"]) for road in roads)
    legacy_disconnected_ids = {
        endpoint["endpointId"]
        for endpoint in endpoints
        if not any(
            endpoint["endpointId"] != other["endpointId"]
            and endpoint["metric"].distance(other["metric"]) <= NEAR_ROAD_THRESHOLD_M
            for other in endpoints
        )
    }
    review_features = []
    candidates = []
    classifications = Counter()
    connected = 0
    priority_counts = Counter()
    p0_road_ids: set[str] = set()
    legacy_reclassified_connected = 0
    legacy_classifications = Counter()
    newly_detected_disconnected = 0

    for endpoint in endpoints:
        road = endpoint["road"]
        road_props = road["feature"]["properties"]
        other_roads = [item for item in roads if item["index"] != road["index"]]
        nearest_road, road_distance, nearest_road_point = _nearest(endpoint["metric"], other_roads)
        if road_distance <= EXACT_TOPOLOGY_M:
            connected += 1
            if endpoint["endpointId"] in legacy_disconnected_ids:
                legacy_reclassified_connected += 1
            continue

        nearest_building, building_distance, nearest_building_point = _nearest(endpoint["metric"], buildings)
        boundary_distance = endpoint["metric"].distance(campus_boundary)
        component_size = component_sizes[union.find(road["index"])]
        safe_snap = False
        suggested_fix = None
        if nearest_road_point is not None and road_distance <= GAP_THRESHOLD_M:
            segment = LineString([endpoint["metric"], nearest_road_point])
            safe_snap = _snap_is_safe(segment, buildings, waters)
            if safe_snap:
                target = wgs84_point(nearest_road_point, center.x, center.y)
                suggested_fix = {
                    "operation": "MERGE_ENDPOINT",
                    "targetRoadId": nearest_road["feature"]["properties"]["externalId"],
                    "targetCoordinate": [round(target.x, 8), round(target.y, 8)],
                    "applied": False,
                }

        if road_distance <= GAP_THRESHOLD_M and safe_snap:
            classification = "LIKELY_TOPOLOGY_GAP"
            main_road = road_props["featureType"] == "ROAD_MAIN" or nearest_road["feature"]["properties"]["featureType"] == "ROAD_MAIN"
            severity = "P0" if road_distance <= 1.0 or main_road or component_size >= 3 else "P1"
            reason = "Endpoint is within 2m of a compatible road and the suggested segment avoids mapped obstacles."
        elif road_distance <= NEAR_ROAD_THRESHOLD_M:
            classification = "NEAR_OTHER_ROAD"
            severity = "P1"
            reason = "Endpoint is near another road, but a conservative snap is not automatically safe."
        elif building_distance <= BUILDING_THRESHOLD_M:
            classification = "NEAR_BUILDING_ENTRANCE"
            severity = "P1" if building_distance <= CANDIDATE_ENTRANCE_THRESHOLD_M else "P2"
            reason = "Endpoint is close to a building boundary and may be a valid entrance terminus."
        elif boundary_distance <= BOUNDARY_THRESHOLD_M:
            classification = "NEAR_CAMPUS_BOUNDARY"
            severity = "P2"
            reason = "Endpoint reaches the campus review boundary and may continue outside the dataset."
        elif component_size <= 2 and road_distance > NEAR_ROAD_THRESHOLD_M:
            classification = "ISOLATED_SEGMENT"
            severity = "P1"
            reason = "Road belongs to a component of at most two features and is separated from the mapped network."
        elif component_size >= 3 and road_distance > NEAR_ROAD_THRESHOLD_M:
            classification = "LIKELY_VALID_TERMINUS"
            severity = "P2"
            reason = "Endpoint belongs to a larger component and has no nearby unsnapped road."
        else:
            classification = "AMBIGUOUS"
            severity = "P2"
            reason = "Available geometry does not support a stronger automatic classification."

        classifications[classification] += 1
        if endpoint["endpointId"] in legacy_disconnected_ids:
            legacy_classifications[classification] += 1
        else:
            newly_detected_disconnected += 1
        priority_counts[severity] += 1
        if severity == "P0":
            p0_road_ids.add(road_props["externalId"])
        nearest_coordinate = None
        if nearest_road_point is not None:
            nearest_wgs84 = wgs84_point(nearest_road_point, center.x, center.y)
            nearest_coordinate = [round(nearest_wgs84.x, 8), round(nearest_wgs84.y, 8)]
        extra = {
            "classification": classification,
            "roadType": road_props["featureType"],
            "nearestRoadId": nearest_road["feature"]["properties"]["externalId"] if nearest_road else None,
            "distanceMeters": round(road_distance, 2) if math.isfinite(road_distance) else None,
            "nearestPoint": nearest_coordinate,
            "nearestBuildingId": nearest_building["feature"]["properties"]["externalId"] if nearest_building else None,
            "buildingDistanceMeters": round(building_distance, 2) if math.isfinite(building_distance) else None,
            "campusBoundaryDistanceMeters": round(boundary_distance, 2),
            "componentEdgeCount": component_size,
            "suggestedFix": suggested_fix,
        }
        review_features.append(review_feature(
            endpoint["point"], endpoint["endpointId"], severity, reason,
            road_props["externalId"], road_props["name"], **extra,
        ))

        if building_distance <= CANDIDATE_ENTRANCE_THRESHOLD_M and nearest_building_point is not None:
            building_props = nearest_building["feature"]["properties"]
            boundary_point = wgs84_point(nearest_building_point, center.x, center.y)
            confidence = "HIGH" if road_props["featureType"] == "ROAD_PEDESTRIAN" and building_distance <= 1.0 else "MEDIUM"
            candidates.append(review_feature(
                boundary_point,
                f"candidate-entrance:{endpoint['endpointId']}",
                "P1" if confidence == "HIGH" else "P2",
                "Road endpoint is within 2m of the mapped building boundary; candidate only.",
                road_props["externalId"],
                f"{building_props['name']} candidate entrance",
                buildingId=building_props["externalId"],
                buildingName=building_props["name"],
                nearestPathId=road_props["externalId"],
                distance=round(building_distance, 2),
                confidence=confidence,
                walkingAccess=None,
                cyclingAccess=None,
                accessible=None,
            ))

    # Preserve multiple possible entrances, but remove near-identical candidates on the same building.
    deduplicated_candidates = []
    for candidate in sorted(candidates, key=lambda item: item["properties"]["distance"]):
        candidate_point = metric(shape(candidate["geometry"]))
        if any(
            existing["properties"]["buildingId"] == candidate["properties"]["buildingId"]
            and metric(shape(existing["geometry"])).distance(candidate_point) <= 4.0
            for existing in deduplicated_candidates
        ):
            continue
        deduplicated_candidates.append(candidate)

    report = {
        "totalEndpoints": len(endpoints),
        "connected": connected,
        "disconnected": len(review_features),
        "classification": dict(sorted(classifications.items())),
        "priority": dict(sorted(priority_counts.items())),
        "p0RoadCount": len(p0_road_ids),
        "p0RoadIds": sorted(p0_road_ids),
        "candidateEntranceCount": len(deduplicated_candidates),
        "legacyEndpointOnlyAudit": {
            "legacyDisconnectedAt4m": len(legacy_disconnected_ids),
            "reclassifiedConnectedToRoadGeometry": legacy_reclassified_connected,
            "remainingLegacyClassifications": dict(sorted(legacy_classifications.items())),
            "newlyDetectedDisconnectedMissedByEndpointOnlyCheck": newly_detected_disconnected,
        },
        "thresholdsMeters": {
            "exactTopology": EXACT_TOPOLOGY_M,
            "likelyGap": GAP_THRESHOLD_M,
            "nearRoad": NEAR_ROAD_THRESHOLD_M,
            "nearBuilding": BUILDING_THRESHOLD_M,
            "candidateEntrance": CANDIDATE_ENTRANCE_THRESHOLD_M,
            "campusBoundary": BOUNDARY_THRESHOLD_M,
        },
    }
    return review_features, report, deduplicated_candidates


def analyze_intersections(layers: dict[str, list[dict[str, Any]]], metric) -> list[dict[str, Any]]:
    result = []
    for road in (item for item in layers["roads"] if item["properties"].get("enabled", True)):
        road_geometry = shape(road["geometry"])
        road_props = road["properties"]
        for building in layers["buildings"]:
            building_geometry = shape(building["geometry"])
            intersection = road_geometry.intersection(building_geometry)
            length = metric(intersection).length if not intersection.is_empty else 0.0
            if length <= 1.0:
                continue
            building_props = building["properties"]
            covered = (road_props.get("covered") == "yes"
                       or road_props.get("tunnel") == "building_passage"
                       or "连廊" in building_props["name"])
            if length <= 2.0:
                cause = "E_BOUNDARY_CONTACT"
                action = "Inspect footprint alignment; do not clip unless the contact is confirmed erroneous."
                severity = "P2"
            elif covered:
                cause = "C_OR_D_MAPPED_COVERED_PASSAGE"
                action = "Retain road and confirm whether it is an indoor, covered, or under-building passage."
                severity = "P1"
            else:
                cause = "A_OR_B_REQUIRES_MANUAL_REVIEW"
                action = "Compare road and building footprint in field/official reference before any override."
                severity = "P0"
            result.append(review_feature(
                intersection,
                f"road-building:{road_props['externalId']}:{building_props['externalId']}",
                severity,
                "Road geometry overlaps a building polygon by more than 1m.",
                road_props["externalId"],
                road_props["name"],
                roadId=road_props["externalId"],
                roadHighway=road_props.get("osmHighway"),
                buildingId=building_props["externalId"],
                buildingName=building_props["name"],
                intersectionLengthMeters=round(length, 2),
                intersectionAreaSquareMeters=round(metric(intersection).area, 2),
                likelyCause=cause,
                recommendedAction=action,
            ))
    return result


def unverified_objects(items: list[dict[str, Any]], object_type: str) -> list[dict[str, Any]]:
    result = []
    for item in items:
        props = item["properties"]
        if props.get("verificationStatus") in {"MANUALLY_REVIEWED", "FIELD_VERIFIED"}:
            continue
        core = core_building(props["name"], props.get("category", "")) if object_type == "BUILDING" else core_poi(props["name"], props.get("category", ""))
        severity = "P0" if core else "P2"
        result.append(review_feature(
            shape(item["geometry"]), f"unverified:{props['externalId']}", severity,
            f"{object_type} has source validation but no manual or field verification.",
            props["externalId"], props["name"],
            category=props.get("category"),
            dataSource=props.get("dataSource"),
            currentVerificationStatus=props.get("verificationStatus"),
            freshnessStatus=props.get("freshnessStatus") if object_type == "POI" else None,
        ))
    return result


def entrance_validation(layers: dict[str, list[dict[str, Any]]], metric) -> list[dict[str, Any]]:
    buildings = {item["properties"]["externalId"]: item for item in layers["buildings"]}
    roads = [metric(shape(item["geometry"])) for item in layers["roads"]]
    result = []
    for entrance in layers["entrances"]:
        props = entrance["properties"]
        building = buildings.get(props.get("buildingExternalId"))
        if not building:
            continue
        point = metric(shape(entrance["geometry"]))
        building_distance = point.distance(metric(shape(building["geometry"]).boundary))
        road_distance = min((point.distance(road) for road in roads), default=math.inf)
        result.append({
            "entranceId": props["externalId"],
            "buildingId": props["buildingExternalId"],
            "buildingBoundaryDistanceMeters": round(building_distance, 2),
            "nearestNetworkDistanceMeters": round(road_distance, 2),
            "boundaryStatus": "OK" if building_distance <= 3 else "WARNING",
            "networkStatus": "P0" if road_distance > 10 else "OK",
        })
    return result


def write_field_review_template(path: Path, buildings: list[dict[str, Any]], pois: list[dict[str, Any]]) -> None:
    rows = []
    for item, object_type in [(item, "BUILDING") for item in buildings] + [(item, "POI") for item in pois]:
        props = item["properties"]
        is_core = core_building(props["name"], props.get("category", "")) if object_type == "BUILDING" else core_poi(props["name"], props.get("category", ""))
        if not is_core:
            continue
        rows.append({
            "object_id": props["externalId"], "object_type": object_type,
            "current_name": props["name"], "confirmed_name": "", "status": "",
            "entrance_lat": "", "entrance_lon": "", "walking_access": "",
            "cycling_access": "", "accessible": "", "notes": "",
        })
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [
            "object_id", "object_type", "current_name", "confirmed_name", "status",
            "entrance_lat", "entrance_lon", "walking_access", "cycling_access", "accessible", "notes",
        ])
        writer.writeheader()
        writer.writerows(rows)


def generate_review_artifacts(layers: dict[str, list[dict[str, Any]]], metric,
                              dataset_dir: Path) -> dict[str, Any]:
    review_dir = dataset_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    endpoint_features, topology, candidates = classify_endpoints(layers, metric)
    intersections = analyze_intersections(layers, metric)
    unverified_buildings = unverified_objects(layers["buildings"], "BUILDING")
    unverified_pois = unverified_objects(layers["pois"], "POI")
    outputs = {
        "topology-gaps.geojson": endpoint_features,
        "road-building-intersections.geojson": intersections,
        "unverified-buildings.geojson": unverified_buildings,
        "unverified-pois.geojson": unverified_pois,
        "candidate-entrances.geojson": candidates,
    }
    for filename, features in outputs.items():
        (review_dir / filename).write_text(
            json.dumps(feature_collection(filename.removesuffix(".geojson"), features), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    building_core = [item for item in layers["buildings"] if core_building(item["properties"]["name"], item["properties"].get("category", ""))]
    poi_core = [item for item in layers["pois"] if core_poi(item["properties"]["name"], item["properties"].get("category", ""))]
    building_reviewed = sum(item["properties"].get("verificationStatus") in {"MANUALLY_REVIEWED", "FIELD_VERIFIED"} for item in building_core)
    poi_reviewed = sum(item["properties"].get("verificationStatus") in {"MANUALLY_REVIEWED", "FIELD_VERIFIED"} for item in poi_core)
    formal_building_ids = {item["properties"].get("buildingExternalId") for item in layers["entrances"]}
    topology.update({
        "generatedAt": date.today().isoformat(),
        "roadBuildingIntersections": len(intersections),
        "intersectionPriority": dict(Counter(item["properties"]["severity"] for item in intersections)),
        "entranceValidation": entrance_validation(layers, metric),
        "qualityMetrics": {
            "coreBuildingVerification": {"reviewed": building_reviewed, "total": len(building_core)},
            "corePoiVerification": {"reviewed": poi_reviewed, "total": len(poi_core)},
            "formalEntranceCoverage": {"buildingsWithEntrance": len(formal_building_ids), "coreBuildings": len(building_core)},
            "candidateEntranceCount": len(candidates),
            "roadP0TopologyIssueCount": topology["priority"].get("P0", 0),
        },
        "gateStatus": "PENDING_MANUAL_IDENTIFICATION",
    })
    metadata_dir = dataset_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    (metadata_dir / "topology-report.json").write_text(json.dumps(topology, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_field_review_template(dataset_dir / "manual" / "field-review-template.csv", layers["buildings"], layers["pois"])
    return topology
