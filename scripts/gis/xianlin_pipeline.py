"""Normalize and validate the NJUPT Xianlin OSM extract."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from shapely.geometry import LineString, Point, Polygon, mapping, shape
from shapely.ops import transform

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "data" / "real" / "xianlin"
MANUAL_DIR = DATASET_DIR / "manual"
CAMPUS_WAY_ID = 89910254
DATASET_ID = "njupt-xianlin-real-v1"
SOURCE_ID = "osm-xianlin-2026-08-22"
FLOOR_HEIGHT_M = 3.3
LOCAL_LON = 118.9259566
LOCAL_LAT = 32.1152716


def stable_id(element: dict[str, Any], suffix: str | None = None) -> str:
    value = f"osm:{element['type']}:{element['id']}"
    return f"{value}:{suffix}" if suffix else value


def tags(element: dict[str, Any]) -> dict[str, str]:
    return element.get("tags") or {}


def osm_name(element: dict[str, Any]) -> str | None:
    value = tags(element).get("name:zh") or tags(element).get("name")
    return value.strip() if value and value.strip() else None


def way_line(element: dict[str, Any]) -> LineString | None:
    coordinates = [(item["lon"], item["lat"]) for item in element.get("geometry", [])]
    return LineString(coordinates) if len(coordinates) >= 2 else None


def way_polygon(element: dict[str, Any]) -> Polygon | None:
    line = way_line(element)
    if line is None or len(line.coords) < 4 or line.coords[0] != line.coords[-1]:
        return None
    return Polygon(line.coords)


def local_metric(geometry):
    cos_lat = math.cos(math.radians(LOCAL_LAT))
    return transform(
        lambda x, y, z=None: ((x - LOCAL_LON) * 111_320 * cos_lat, (y - LOCAL_LAT) * 110_540),
        geometry,
    )


def building_category(element: dict[str, Any]) -> str:
    value = tags(element)
    text = " ".join(filter(None, [osm_name(element), value.get("amenity"), value.get("building")]))
    if any(key in text for key in ("图书馆", "library")):
        return "LIBRARY"
    if any(key in text for key in ("食堂", "餐厅", "restaurant", "canteen", "cafe")):
        return "DINING"
    if any(key in text for key in ("宿舍", "公寓", "dormitory", "residential")):
        return "DORMITORY"
    if any(key in text for key in ("体育", "gym", "sports")):
        return "SPORT"
    if any(key in text for key in ("医院", "医务", "clinic", "hospital")):
        return "MEDICAL"
    if any(key in text for key in ("行政", "办公", "administration", "office")):
        return "ADMINISTRATION"
    if any(key in text for key in ("教学", "实验", "学院", "学科", "楼", "university")):
        return "TEACHING"
    return "OTHER"


def poi_category(element: dict[str, Any]) -> str:
    value = tags(element)
    amenity = value.get("amenity", "")
    if amenity in {"restaurant", "fast_food", "cafe", "food_court"}:
        return "DINING"
    if amenity in {"library"}:
        return "LIBRARY"
    if amenity in {"clinic", "hospital", "doctors", "pharmacy"}:
        return "MEDICAL"
    if value.get("shop"):
        return "SHOP"
    if amenity in {"atm", "bank", "post_office", "community_centre"}:
        return "SERVICE"
    return "OTHER"


def height_properties(element: dict[str, Any]) -> dict[str, Any]:
    value = tags(element)
    raw_height = value.get("height", "").lower().replace("meters", "").replace("meter", "").replace("m", "").strip()
    try:
        height = float(raw_height)
        if 0 < height < 300:
            return {"height": round(height, 2), "heightSource": "OSM_HEIGHT"}
    except ValueError:
        pass
    try:
        levels = float(value.get("building:levels", ""))
        if 0 < levels < 80:
            return {
                "height": round(levels * FLOOR_HEIGHT_M, 2),
                "heightSource": "ESTIMATED_FROM_LEVELS",
            }
    except ValueError:
        pass
    return {"heightSource": "UNKNOWN"}


def base_properties(element: dict[str, Any], feature_type: str, name: str) -> dict[str, Any]:
    return {
        "featureType": feature_type,
        "campusCode": "NJUPT_XIANLIN",
        "externalId": stable_id(element),
        "name": name,
        "dataSource": "OPENSTREETMAP",
        "verificationStatus": "SOURCE_VERIFIED",
        "sourceId": SOURCE_ID,
        "sourceUpdatedAt": tags(element).get("check_date"),
        "osmType": element["type"],
        "osmId": element["id"],
    }


def feature(geometry, properties: dict[str, Any]) -> dict[str, Any]:
    return {"type": "Feature", "id": properties["externalId"], "properties": properties, "geometry": mapping(geometry)}


def root_metadata(layer: str) -> dict[str, Any]:
    return {
        "datasetId": DATASET_ID,
        "layer": layer,
        "dataSource": "OPENSTREETMAP",
        "sourceId": SOURCE_ID,
        "license": "ODbL-1.0",
        "requiredAttribution": "© OpenStreetMap contributors",
        "retrievedAt": "2026-08-22",
        "coordinateSystem": "EPSG:4326",
        "verificationStatus": "SOURCE_VERIFIED",
    }


def collection(layer: str, features: list[dict[str, Any]]) -> dict[str, Any]:
    return {"type": "FeatureCollection", "name": f"{DATASET_ID}-{layer}", "metadata": root_metadata(layer), "features": features}


def load_manual() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for filename in ("building-names.json", "building-heights.json", "building-overrides.json", "poi-overrides.json"):
        path = MANUAL_DIR / filename
        if path.is_file():
            for key, value in json.loads(path.read_text(encoding="utf-8")).items():
                result.setdefault(key, {}).update(value)
    return result


def load_aliases() -> dict[str, list[str]]:
    path = MANUAL_DIR / "place-aliases.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def apply_aliases(item: dict[str, Any], aliases: dict[str, list[str]]) -> dict[str, Any]:
    name = item["properties"].get("name")
    if name in aliases:
        item["properties"]["aliases"] = aliases[name]
    return item


def load_manual_entrances() -> list[dict[str, Any]]:
    path = MANUAL_DIR / "entrances.geojson"
    if not path.is_file():
        return []
    collection_value = json.loads(path.read_text(encoding="utf-8"))
    if collection_value.get("type") != "FeatureCollection":
        raise ValueError("manual/entrances.geojson must be a FeatureCollection")
    result = []
    for item in collection_value.get("features", []):
        properties = item.setdefault("properties", {})
        properties["featureType"] = "ENTRANCE"
        properties.setdefault("dataSource", "MANUAL")
        properties.setdefault("sourceId", "manual-xianlin-v1")
        properties.setdefault("verificationStatus", "PENDING_FIELD_VERIFICATION")
        result.append(item)
    return result


def load_review_manifest() -> dict[str, dict[str, Any]]:
    path = MANUAL_DIR / "review-manifest.json"
    if not path.is_file():
        return {}
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return {item["objectId"]: item for item in manifest.get("reviews", [])}


def apply_review(item: dict[str, Any], reviews: dict[str, dict[str, Any]]) -> dict[str, Any]:
    external_id = item["properties"]["externalId"]
    review = reviews.get(external_id)
    if not review:
        return item
    status = review.get("status")
    if status not in {"MANUALLY_REVIEWED", "FIELD_VERIFIED"}:
        raise ValueError(f"Review {external_id} must be MANUALLY_REVIEWED or FIELD_VERIFIED")
    if not review.get("reviewedAt"):
        raise ValueError(f"Review {external_id} must include reviewedAt")
    item["properties"].update({
        "verificationStatus": status,
        "verifiedAt": review["reviewedAt"],
        "verificationNote": review.get("notes", ""),
        "reviewedBy": review.get("reviewedBy", "manual-review"),
    })
    return item


def road_access_properties(element: dict[str, Any]) -> dict[str, Any]:
    value = tags(element)

    def explicit(tag_name: str) -> bool | None:
        tag_value = value.get(tag_name)
        if tag_value in {"yes", "designated", "permissive"}:
            return True
        if tag_value in {"no", "private"}:
            return False
        return None

    return {
        "walkingAccess": explicit("foot"),
        "cyclingAccess": explicit("bicycle"),
        "vehicleAccess": explicit("motor_vehicle") if value.get("motor_vehicle") else explicit("vehicle"),
        "accessSource": "OSM_EXPLICIT_TAGS" if any(value.get(key) for key in ("foot", "bicycle", "motor_vehicle", "vehicle")) else "UNKNOWN",
        "covered": value.get("covered"),
        "tunnel": value.get("tunnel"),
        "bridge": value.get("bridge"),
        "layer": value.get("layer"),
    }


def apply_road_overrides(roads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    path = MANUAL_DIR / "road-overrides.geojson"
    if not path.is_file():
        return roads
    collection_value = json.loads(path.read_text(encoding="utf-8"))
    if collection_value.get("type") != "FeatureCollection":
        raise ValueError("manual/road-overrides.geojson must be a FeatureCollection")
    by_id = {item["properties"]["externalId"]: item for item in roads}
    for override in collection_value.get("features", []):
        properties = override.get("properties") or {}
        operation = properties.get("operation")
        source_id = properties.get("sourceObjectId")
        if operation == "ADD_MANUAL_PATH":
            external_id = properties.get("externalId")
            if not external_id or not external_id.startswith("manual:xianlin:road:"):
                raise ValueError("ADD_MANUAL_PATH requires manual:xianlin:road:* externalId")
            properties.update({
                "dataSource": "MANUAL", "sourceId": "manual-xianlin-v1",
                "verificationStatus": properties.get("verificationStatus", "MANUALLY_REVIEWED"),
                "featureType": properties.get("featureType", "ROAD_PEDESTRIAN"),
            })
            by_id[external_id] = override
            continue
        if source_id not in by_id:
            raise ValueError(f"Road override cannot find sourceObjectId {source_id}")
        target = by_id[source_id]
        if operation == "DISABLE_SOURCE_OBJECT":
            target["properties"]["enabled"] = False
        elif operation in {"REPLACE_GEOMETRY", "MERGE_ENDPOINT"}:
            if not override.get("geometry"):
                raise ValueError(f"{operation} requires replacement geometry")
            target["geometry"] = override["geometry"]
        else:
            raise ValueError(f"Unsupported road override operation: {operation}")
        target["properties"].update({
            "verificationStatus": properties.get("verificationStatus", "MANUALLY_REVIEWED"),
            "verifiedAt": properties.get("reviewedAt"),
            "verificationNote": properties.get("reason", ""),
            "reviewedBy": properties.get("reviewedBy", "manual-review"),
            "manualOperation": operation,
        })
    return list(by_id.values())


def apply_override(item: dict[str, Any], overrides: dict[str, dict[str, Any]]) -> dict[str, Any]:
    external_id = item["properties"]["externalId"]
    if external_id in overrides:
        item["properties"].update(overrides[external_id])
    return item


GENERIC_NAMES = {
    "Building", "Dormitory", "Residential Building", "Student Residence",
    "Student Apartment", "宿舍", "学生宿舍", "公寓", "办公楼", "教学楼",
    "门卫", "连廊", "主席台",
}


def dormitory_candidate(name: str, category: str) -> dict[str, str] | None:
    if category != "DORMITORY":
        return None
    match = re.match(r"^(\d{1,2})(?:\s|号|栋|楼|$)", name)
    if match:
        number = match.group(1)
        return {
            "number": number,
            "displayName": f"{number}号楼",
            "confidence": "HIGH",
            "evidence": f"OSM source name begins with the explicit number {number}; no spatial-order inference used",
        }
    return {
        "number": "",
        "displayName": name,
        "confidence": "UNKNOWN",
        "evidence": "Dormitory category is source-backed, but the source name contains no numeric identifier",
    }


def apply_naming_semantics(item: dict[str, Any]) -> dict[str, Any]:
    props = item["properties"]
    name = props.get("name", "")
    category = props.get("category", "")
    props.setdefault("officialName", None)
    props.setdefault("displayName", name)
    props.setdefault("aliases", [])
    props.setdefault("labelVisible", bool(name) and not name.startswith("未命名"))

    candidate = dormitory_candidate(name, category)
    if candidate:
        props["dormitoryCandidate"] = candidate
        if candidate["number"]:
            props["displayName"] = candidate["displayName"]
            props["aliases"] = list(dict.fromkeys([
                *props.get("aliases", []), candidate["displayName"],
                f"{candidate['number']}号宿舍",
            ]))
        props["labelVisible"] = candidate["confidence"] == "HIGH"

    if (name in GENERIC_NAMES
            or len(name) > 16
            or (props.get("featureType") == "BUILDING" and any(token in name for token in ("学院", "教学部")))):
        props["labelVisible"] = False
    return item


def normalize(raw: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int]]:
    elements = raw["elements"]
    campus_element = next(item for item in elements if item["type"] == "way" and item["id"] == CAMPUS_WAY_ID)
    boundary = way_polygon(campus_element)
    if boundary is None or not boundary.is_valid:
        raise ValueError("OSM campus boundary way is missing or invalid")
    review_area = boundary.buffer(0.00045)
    overrides = load_manual()
    aliases = load_aliases()
    reviews = load_review_manifest()
    layers: dict[str, list[dict[str, Any]]] = {name: [] for name in ("campus", "buildings", "roads", "surfaces", "pois", "entrances")}
    excluded = Counter()

    campus_props = base_properties(campus_element, "CAMPUS_BOUNDARY", "南京邮电大学仙林校区")
    campus_props["priority"] = 100
    layers["campus"].append(feature(boundary, campus_props))

    for element in elements:
        value = tags(element)
        if element["type"] != "way" or "building" not in value:
            continue
        polygon = way_polygon(element)
        if polygon is None or polygon.is_empty or not polygon.representative_point().within(review_area):
            excluded["building_outside_or_invalid"] += 1
            continue
        name = osm_name(element)
        if not name:
            excluded["unnamed_building"] += 1
            continue
        properties = base_properties(element, "BUILDING", name)
        properties.update({"aliases": [], "category": building_category(element), "minHeight": 0, "color": "#D8DDE1"})
        properties.update(height_properties(element))
        item = apply_naming_semantics(apply_aliases(apply_override(feature(polygon, properties), overrides), aliases))
        layers["buildings"].append(item)

    for element in elements:
        value = tags(element)
        if element["type"] == "way" and value.get("highway"):
            line = way_line(element)
            if line is None or not line.intersects(review_area):
                continue
            pedestrian = value["highway"] in {"footway", "path", "pedestrian", "steps", "cycleway", "track"}
            feature_type = "ROAD_PEDESTRIAN" if pedestrian else "ROAD_MAIN"
            name = osm_name(element) or ("未命名步道" if pedestrian else "未命名道路")
            properties = base_properties(element, feature_type, name)
            properties["priority"] = 45 if not pedestrian else 20
            properties["osmHighway"] = value["highway"]
            properties.update(road_access_properties(element))
            clipped = line.intersection(review_area)
            if clipped.is_empty or not clipped.is_valid or not clipped.is_simple:
                excluded["invalid_or_non_simple_road"] += 1
                continue
            layers["roads"].append(feature(clipped, properties))

        polygon = way_polygon(element) if element["type"] == "way" else None
        if polygon is not None and polygon.representative_point().within(review_area) and "building" not in value:
            surface_type = None
            if value.get("natural") == "water" or value.get("water"):
                surface_type = "WATER"
            elif value.get("leisure") in {"pitch", "track", "stadium", "sports_centre"}:
                surface_type = "SPORT"
            elif value.get("landuse") in {"grass", "meadow", "forest", "recreation_ground"} or value.get("leisure") in {"park", "garden"}:
                surface_type = "GREEN"
            elif value.get("place") == "square":
                surface_type = "PLAZA"
            if surface_type:
                fallback = {"WATER": "未命名水体", "SPORT": "未命名运动设施", "GREEN": "未命名绿地", "PLAZA": "未命名广场"}[surface_type]
                properties = base_properties(element, surface_type, osm_name(element) or fallback)
                properties["priority"] = 35
                layers["surfaces"].append(feature(polygon, properties))

        if element["type"] == "node" and (value.get("amenity") or value.get("shop")) and osm_name(element):
            point = Point(element["lon"], element["lat"])
            if point.within(review_area):
                properties = base_properties(element, "POI", osm_name(element) or "未命名地点")
                properties.update({"aliases": [], "keywords": [], "category": poi_category(element), "priority": 40, "positionSource": "OSM_NODE", "freshnessStatus": "SOURCE_ONLY", "lastVerifiedAt": None})
                item = apply_naming_semantics(apply_aliases(apply_override(feature(point, properties), overrides), aliases))
                layers["pois"].append(item)

    # Link source POI nodes to a containing building when the spatial match is unambiguous.
    for poi in layers["pois"]:
        point_geometry = shape(poi["geometry"])
        containing = [
            building for building in layers["buildings"]
            if point_geometry.within(shape(building["geometry"]))
        ]
        if len(containing) == 1:
            poi["properties"]["buildingExternalId"] = containing[0]["properties"]["externalId"]
            poi["properties"]["buildingLinkSource"] = "POINT_WITHIN_SINGLE_BUILDING"

    # Named facility buildings become POIs linked to the source building. Position is explicitly derived.
    poi_ids = {item["properties"]["externalId"] for item in layers["pois"]}
    generated_groups: set[str] = set()
    for item in layers["buildings"]:
        category = item["properties"]["category"]
        if category not in {"LIBRARY", "DINING", "MEDICAL", "SPORT", "ADMINISTRATION", "TEACHING"}:
            continue
        group_id = item["properties"].get("poiGroupId") or item["properties"]["externalId"]
        if group_id in generated_groups:
            continue
        generated_groups.add(group_id)
        source_id = f"{item['properties']['externalId']}:poi"
        if source_id in poi_ids:
            continue
        point = shape(item["geometry"]).representative_point()
        properties = dict(item["properties"])
        related = [
            candidate["properties"]["externalId"] for candidate in layers["buildings"]
            if (candidate["properties"].get("poiGroupId") or candidate["properties"]["externalId"]) == group_id
        ]
        properties.update({"externalId": source_id, "featureType": "POI", "buildingExternalId": item["properties"]["externalId"], "relatedBuildingExternalIds": related, "keywords": [], "priority": 45, "positionSource": "DERIVED_REPRESENTATIVE_POINT"})
        poi_display_name = properties.get("displayName") or properties.get("name", "")
        properties["labelVisible"] = poi_display_name not in GENERIC_NAMES and len(poi_display_name) <= 16
        for key in ("height", "heightSource", "minHeight", "color"):
            properties.pop(key, None)
        layers["pois"].append(feature(point, properties))

    layers["entrances"].extend(load_manual_entrances())
    layers["roads"] = apply_road_overrides(layers["roads"])
    for layer_items in layers.values():
        for item in layer_items:
            apply_review(item, reviews)

    return layers, dict(excluded)


def validate(layers: dict[str, list[dict[str, Any]]], excluded: dict[str, int]) -> dict[str, Any]:
    all_features = [item for values in layers.values() for item in values]
    boundary = shape(layers["campus"][0]["geometry"])
    review_area = boundary.buffer(0.00045)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_geometry: dict[bytes, str] = {}
    names = defaultdict(list)
    buildings = [shape(item["geometry"]) for item in layers["buildings"]]

    for item in all_features:
        props = item["properties"]
        item_id = props["externalId"]
        geometry = shape(item["geometry"])
        if item_id in seen_ids:
            errors.append({"id": item_id, "reason": "duplicate externalId"})
        seen_ids.add(item_id)
        if geometry.is_empty or not geometry.is_valid or not geometry.is_simple:
            errors.append({"id": item_id, "reason": "invalid, empty or non-simple geometry"})
        if not all(math.isfinite(value) for value in geometry.bounds) or (
            geometry.bounds[0] < -180
            or geometry.bounds[2] > 180
            or geometry.bounds[1] < -90
            or geometry.bounds[3] > 90
        ):
            errors.append({"id": item_id, "reason": "coordinate outside WGS84 longitude/latitude range"})
        if not geometry.intersects(review_area):
            errors.append({"id": item_id, "reason": "outside campus review buffer"})
        if geometry.wkb in seen_geometry:
            warnings.append({"id": item_id, "reason": f"identical geometry to {seen_geometry[geometry.wkb]}"})
        seen_geometry[geometry.wkb] = item_id
        names[props.get("name", "")].append(item_id)
        if props.get("name", "").startswith("未命名"):
            warnings.append({"id": item_id, "reason": "missing verified name"})
        if props["featureType"] == "BUILDING":
            area = local_metric(geometry).area
            if area < 20 or area > 100_000:
                warnings.append({"id": item_id, "reason": f"building area {area:.1f}m² outside review threshold"})
            height = props.get("height")
            if height is not None and height < 0:
                errors.append({"id": item_id, "reason": "negative building height"})

    road_features = layers["roads"]
    road_crossings = []
    endpoints = []
    for item in road_features:
        line = shape(item["geometry"])
        metric_line = local_metric(line)
        if metric_line.length < 2:
            errors.append({"id": item["properties"]["externalId"], "reason": "road shorter than 2m"})
        parts = list(metric_line.geoms) if hasattr(metric_line, "geoms") else [metric_line]
        for part in parts:
            if len(part.coords) >= 2:
                endpoints.extend([Point(part.coords[0]), Point(part.coords[-1])])
        crossing_count = sum(1 for building in buildings if local_metric(line.intersection(building)).length > 1)
        if crossing_count:
            road_crossings.append({"id": item["properties"]["externalId"], "buildingIntersections": crossing_count})
    dangling = sum(1 for index, point in enumerate(endpoints) if not any(index != other and point.distance(candidate) <= 4 for other, candidate in enumerate(endpoints)))
    duplicate_names = {name: ids for name, ids in names.items() if name and len(ids) > 1 and not name.startswith("未命名")}
    error_ids = {item["id"] for item in errors}
    by_type = Counter(item["properties"]["featureType"] for item in all_features)
    report = {
        "datasetId": DATASET_ID,
        "generatedAt": date.today().isoformat(),
        "total": len(all_features),
        "valid": len(all_features) - len(error_ids),
        "warning": len(warnings) + len(road_crossings),
        "error": len(errors),
        "byFeatureType": dict(sorted(by_type.items())),
        "geometryErrors": errors,
        "coordinateErrors": [item for item in errors if "coordinate" in item["reason"]],
        "coordinateSystem": "EPSG:4326 (WGS84 longitude, latitude)",
        "outOfBounds": [item for item in errors if "outside" in item["reason"]],
        "duplicates": {"names": duplicate_names, "identicalGeometry": [item for item in warnings if "identical" in item["reason"]]},
        "missingNames": [item for item in warnings if "missing verified name" in item["reason"]],
        "unverified": sum(item["properties"].get("verificationStatus") == "UNVERIFIED" for item in all_features),
        "excludedRaw": excluded,
        "roadConnectivity": {"roadCount": len(road_features), "endpointCount": len(endpoints), "danglingEndpointsAt4m": dangling},
        "roadBuildingIntersections": road_crossings,
        "warnings": warnings,
    }
    return report


def write_outputs(raw_path: Path) -> dict[str, Any]:
    from gis_review import generate_review_artifacts
    from naming_audit import generate_naming_artifacts

    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    layers, excluded = normalize(raw)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    for layer, items in layers.items():
        (DATASET_DIR / f"{layer}.geojson").write_text(json.dumps(collection(layer, items), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = validate(layers, excluded)
    topology = generate_review_artifacts(layers, local_metric, DATASET_DIR)
    naming = generate_naming_artifacts(layers, raw, local_metric, DATASET_DIR)
    report["naming"] = naming
    report["topologyClassification"] = {
        "connected": topology["connected"],
        "disconnected": topology["disconnected"],
        "classification": topology["classification"],
        "priority": topology["priority"],
        "p0RoadCount": topology["p0RoadCount"],
    }
    report["entranceCoverage"] = topology["qualityMetrics"]["formalEntranceCoverage"]
    report["manualVerificationCoverage"] = {
        "coreBuildings": topology["qualityMetrics"]["coreBuildingVerification"],
        "corePois": topology["qualityMetrics"]["corePoiVerification"],
    }
    metadata = DATASET_DIR / "metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / "validation-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report["error"]:
        raise SystemExit(f"GIS validation failed with {report['error']} errors")
    print(json.dumps({"total": report["total"], "byFeatureType": report["byFeatureType"], "warnings": report["warning"]}, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate"))
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw" / "osm" / "xianlin-2026-08-22.overpass.json")
    args = parser.parse_args()
    if args.command == "build":
        write_outputs(args.raw.resolve())
    else:
        layers = {name: json.loads((DATASET_DIR / f"{name}.geojson").read_text(encoding="utf-8"))["features"] for name in ("campus", "buildings", "roads", "surfaces", "pois", "entrances")}
        report = validate(layers, {})
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if report["error"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
