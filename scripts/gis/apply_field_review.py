"""Convert a completed field-review CSV into traceable manual overrides."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANUAL_DIR = ROOT / "data" / "real" / "xianlin" / "manual"
REVIEWED_STATUSES = {"MANUALLY_REVIEWED", "FIELD_VERIFIED"}


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
                  reviewed_by: str) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
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
        reviews.append({
            "objectId": object_id,
            "status": status,
            "reviewedAt": reviewed_at,
            "reviewedBy": reviewed_by,
            "notes": notes,
        })
        confirmed_name = row.get("confirmed_name", "").strip()
        if confirmed_name:
            target = building_overrides if object_type == "BUILDING" else poi_overrides
            target[object_id] = {
                "name": confirmed_name,
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
                "name": f"{confirmed_name or row.get('current_name', '').strip()}主要入口",
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
    return reviews, building_overrides, poi_overrides, entrances


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_MANUAL_DIR)
    parser.add_argument("--reviewed-at", required=True, help="ISO-8601 date or timestamp from the actual review")
    parser.add_argument("--reviewed-by", default="manual-review")
    args = parser.parse_args()
    result = apply_csv(args.input.resolve(), args.output_dir.resolve(), args.reviewed_at, args.reviewed_by)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
