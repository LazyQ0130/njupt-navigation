"""Convert a completed field-review CSV into traceable manual overrides."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANUAL_DIR = ROOT / "data" / "real" / "xianlin" / "manual"
REVIEWED_STATUSES = {"MANUALLY_REVIEWED", "FIELD_VERIFIED"}
REVIEW_METHODS = {"OFFICIAL_REFERENCE", "USER_MANUAL_REVIEW", "FIELD_CHECK"}


def optional_boolean(value: str) -> bool | None:
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value}")


def load_json(path: Path, fallback: Any) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else fallback


def build_updates(rows: list[dict[str, str]], reviewed_at: str,
                  reviewed_by: str, review_method: str | None = None
                  ) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    reviews = []
    building_overrides: dict[str, Any] = {}
    poi_overrides: dict[str, Any] = {}
    entrances = []
    for row in rows:
        status = row.get("status", "").strip().upper()
        if not status:
            continue
        if status not in REVIEWED_STATUSES:
            raise ValueError(f"{row.get('object_id')}: status must be MANUALLY_REVIEWED or FIELD_VERIFIED")
        object_id = row["object_id"].strip()
        object_type = row["object_type"].strip().upper()
        notes = row.get("notes", "").strip()
        method = row.get("review_method", "").strip().upper() or review_method or (
            "FIELD_CHECK" if status == "FIELD_VERIFIED" else "USER_MANUAL_REVIEW"
        )
        if method not in REVIEW_METHODS:
            raise ValueError(f"{object_id}: unsupported reviewMethod {method}")
        confirmed_name = row.get("confirmed_name", "").strip()
        official_name = row.get("confirmed_official_name", "").strip() or confirmed_name
        display_name = row.get("confirmed_display_name", "").strip() or official_name
        name_verified = optional_boolean(row.get("name_verified", ""))
        geometry_verified = optional_boolean(row.get("geometry_verified", ""))
        reviews.append({
            "objectId": object_id,
            "status": status,
            "reviewedAt": reviewed_at,
            "reviewMethod": method,
            "reviewedBy": reviewed_by,
            "nameVerified": bool(official_name) if name_verified is None else name_verified,
            "geometryVerified": False if geometry_verified is None else geometry_verified,
            "notes": notes,
        })
        if official_name:
            target = building_overrides if object_type == "BUILDING" else poi_overrides
            target[object_id] = {
                "name": official_name,
                "officialName": official_name,
                "displayName": display_name,
                "aliases": parse_aliases(row.get("aliases", "")),
                "verificationStatus": status,
                "verifiedAt": reviewed_at,
                "verificationNote": notes,
                "reviewedBy": reviewed_by,
            }
        latitude = row.get("entrance_lat", "").strip()
        longitude = row.get("entrance_lon", "").strip()
        if bool(latitude) != bool(longitude):
            raise ValueError(f"{object_id}: entrance_lat and entrance_lon must be supplied together")
        if not latitude:
            continue
        if object_type != "BUILDING":
            raise ValueError(f"{object_id}: only BUILDING rows can create formal entrances")
        lat_value = float(latitude)
        lon_value = float(longitude)
        if not (-90 <= lat_value <= 90 and -180 <= lon_value <= 180):
            raise ValueError(f"{object_id}: entrance coordinate is outside WGS84 range")
        entrance_id = f"manual:xianlin:entrance:{object_id.replace(':', '-')}"
        entrances.append({
            "type": "Feature",
            "id": entrance_id,
            "geometry": {"type": "Point", "coordinates": [lon_value, lat_value]},
            "properties": {
                "externalId": entrance_id,
                "featureType": "ENTRANCE",
                "buildingExternalId": object_id,
                "name": f"{display_name or row.get('current_name', '').strip()}主要入口",
                "walkingAccess": optional_boolean(row.get("walking_access", "")),
                "cyclingAccess": optional_boolean(row.get("cycling_access", "")),
                "accessible": optional_boolean(row.get("accessible", "")),
                "vehicleAccess": None,
                "openingHours": None,
                "dataSource": "MANUAL",
                "sourceId": "field-review-v1",
                "verificationStatus": status,
                "verifiedAt": reviewed_at,
                "verificationNote": notes,
                "reviewedBy": reviewed_by,
            },
        })
        reviews.append({
            "objectId": entrance_id,
            "status": status,
            "reviewedAt": reviewed_at,
            "reviewMethod": method,
            "reviewedBy": reviewed_by,
            "nameVerified": True,
            "geometryVerified": True,
            "notes": notes,
        })
    return reviews, building_overrides, poi_overrides, entrances


def parse_aliases(value: str) -> list[str]:
    return list(dict.fromkeys(
        alias.strip() for alias in re.split(r"[|,;，；]", value or "") if alias.strip()
    ))


def build_dormitory_updates(rows: list[dict[str, str]], reviewed_at: str
                             ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    building_names: dict[str, Any] = {}
    for row in rows:
        status = row.get("status", "").strip().upper()
        if status in {"", "NEEDS_MANUAL_CONFIRMATION"}:
            continue
        object_id = row.get("osm_id", "").strip()
        if status not in REVIEWED_STATUSES:
            raise ValueError(f"{object_id}: status must be MANUALLY_REVIEWED or FIELD_VERIFIED")
        number = row.get("confirmed_number", "").strip()
        display_name = row.get("confirmed_display_name", "").strip()
        if not number or not display_name:
            raise ValueError(f"{object_id}: confirmed_number and confirmed_display_name are required")
        if not number.isdigit() or not 1 <= int(number) <= 99:
            raise ValueError(f"{object_id}: confirmed_number must be a campus building number")
        method = "FIELD_CHECK" if status == "FIELD_VERIFIED" else "USER_MANUAL_REVIEW"
        notes = row.get("notes", "").strip()
        aliases = parse_aliases(row.get("aliases", ""))
        safe_aliases = list(dict.fromkeys([display_name, f"{number}号宿舍", *aliases]))
        official_name = f"{number}号学生宿舍"
        reviews.append({
            "objectId": object_id,
            "status": status,
            "reviewedAt": reviewed_at,
            "reviewMethod": method,
            "reviewedBy": "manual-review",
            "nameVerified": True,
            "geometryVerified": False,
            "notes": notes,
        })
        building_names[object_id] = {
            "officialName": official_name,
            "displayName": display_name,
            "aliases": safe_aliases,
            "category": "DORMITORY",
            "labelVisible": True,
            "verificationStatus": status,
            "source": method,
            "sourceUrl": None,
            "reviewStatus": status,
            "reviewedAt": reviewed_at,
            "notes": notes,
        }
    return reviews, building_names


def apply_csv(input_path: Path, output_dir: Path, reviewed_at: str, reviewed_by: str) -> dict[str, int]:
    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    reviews, building_updates, poi_updates, entrance_updates = build_updates(rows, reviewed_at, reviewed_by)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "review-manifest.json"
    manifest = load_json(manifest_path, {"schemaVersion": "1.0", "reviews": []})
    review_by_id = {item["objectId"]: item for item in manifest.get("reviews", [])}
    review_by_id.update({item["objectId"]: item for item in reviews})
    manifest["reviews"] = sorted(review_by_id.values(), key=lambda item: item["objectId"])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for filename, updates in (("building-overrides.json", building_updates), ("poi-overrides.json", poi_updates)):
        path = output_dir / filename
        current = load_json(path, {})
        current.update(updates)
        path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    entrance_path = output_dir / "entrances.geojson"
    entrance_collection = load_json(entrance_path, {"type": "FeatureCollection", "features": []})
    entrance_by_id = {item["properties"]["externalId"]: item for item in entrance_collection.get("features", [])}
    entrance_by_id.update({item["properties"]["externalId"]: item for item in entrance_updates})
    entrance_collection["features"] = sorted(entrance_by_id.values(), key=lambda item: item["properties"]["externalId"])
    entrance_path.write_text(json.dumps(entrance_collection, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "reviews": len(reviews),
        "buildingOverrides": len(building_updates),
        "poiOverrides": len(poi_updates),
        "entrances": len(entrance_updates),
    }


def apply_dormitory_csv(input_path: Path, output_dir: Path, reviewed_at: str) -> dict[str, int]:
    with input_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    reviews, building_updates = build_dormitory_updates(rows, reviewed_at)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "review-manifest.json"
    manifest = load_json(manifest_path, {"schemaVersion": "1.0", "reviews": []})
    review_by_id = {item["objectId"]: item for item in manifest.get("reviews", [])}
    review_by_id.update({item["objectId"]: item for item in reviews})
    manifest["reviews"] = sorted(review_by_id.values(), key=lambda item: item["objectId"])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    names_path = output_dir / "building-names.json"
    current = load_json(names_path, {})
    current.update(building_updates)
    names_path.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"reviews": len(reviews), "buildingNames": len(building_updates)}


def main() -> None:
    parser = argparse.ArgumentParser()
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--input", type=Path)
    inputs.add_argument("--dormitory-input", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_MANUAL_DIR)
    parser.add_argument("--reviewed-at", required=True, help="ISO-8601 date or timestamp from the actual review")
    parser.add_argument("--reviewed-by", default="manual-review")
    args = parser.parse_args()
    if args.dormitory_input:
        result = apply_dormitory_csv(
            args.dormitory_input.resolve(), args.output_dir.resolve(), args.reviewed_at,
        )
    else:
        result = apply_csv(
            args.input.resolve(), args.output_dir.resolve(), args.reviewed_at, args.reviewed_by,
        )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
