"""Generate reproducible naming and dormitory review artifacts for Xianlin GIS data."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from shapely.geometry import mapping, shape


ISSUE_TYPES = (
    "UNNAMED", "GENERIC_NAME", "DUPLICATE_NAME", "OVERLONG_NAME", "AMBIGUOUS_NAME",
    "TECHNICAL_NAME", "MISSING_DISPLAY_NAME", "MISSING_ALIAS", "DORMITORY_UNKNOWN_NUMBER",
    "BUILDING_POI_DUPLICATE",
)
GENERIC_NAMES = {
    "Building", "Dormitory", "Residential Building", "Student Residence", "Student Apartment",
    "宿舍", "学生宿舍", "公寓", "办公楼", "教学楼", "门卫", "连廊", "主席台",
}
DORMITORY_FIELDS = (
    "osm_id", "current_name", "current_category", "longitude", "latitude", "candidate_number",
    "candidate_display_name", "confidence", "evidence", "confirmed_number",
    "confirmed_display_name", "aliases", "status", "notes",
)


def _raw_index(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        f"osm:{item['type']}:{item['id']}": item
        for item in raw.get("elements", [])
        if item.get("type") and item.get("id") is not None
    }


def _duplicate_groups(items: list[dict[str, Any]], field: str = "name") -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for item in items:
        props = item["properties"]
        value = props.get(field) or props.get("name")
        if value:
            groups[value].append(props["externalId"])
    return {name: ids for name, ids in groups.items() if len(ids) > 1}


def _issues(buildings: list[dict[str, Any]], pois: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {key: [] for key in ISSUE_TYPES}
    all_items = buildings + pois
    duplicate_ids = {item_id for ids in _duplicate_groups(buildings).values() for item_id in ids}
    building_names = defaultdict(list)
    poi_names = defaultdict(list)
    for item in buildings:
        building_names[item["properties"].get("displayName") or item["properties"].get("name")].append(item)
    for item in pois:
        poi_names[item["properties"].get("displayName") or item["properties"].get("name")].append(item)

    for item in all_items:
        props = item["properties"]
        item_id = props["externalId"]
        name = (props.get("name") or "").strip()
        display_name = (props.get("displayName") or "").strip()
        if not name or name.startswith("未命名"):
            result["UNNAMED"].append(item_id)
        if name in GENERIC_NAMES:
            result["GENERIC_NAME"].append(item_id)
        if item_id in duplicate_ids:
            result["DUPLICATE_NAME"].append(item_id)
        if len(name) > 16:
            result["OVERLONG_NAME"].append(item_id)
        if any(token in name for token in ("、", "-新大楼", "办公楼办公楼")):
            result["AMBIGUOUS_NAME"].append(item_id)
        if name.lower().startswith(("osm:", "way:", "node:")):
            result["TECHNICAL_NAME"].append(item_id)
        if not display_name:
            result["MISSING_DISPLAY_NAME"].append(item_id)
        if not props.get("aliases") and props.get("featureType") in {"BUILDING", "POI"}:
            result["MISSING_ALIAS"].append(item_id)
        candidate = props.get("dormitoryCandidate")
        if props.get("category") == "DORMITORY" and (not candidate or not candidate.get("number")):
            result["DORMITORY_UNKNOWN_NUMBER"].append(item_id)

    shared_names = set(building_names) & set(poi_names)
    for name in shared_names:
        result["BUILDING_POI_DUPLICATE"].extend(
            [item["properties"]["externalId"] for item in building_names[name] + poi_names[name]]
        )
    return result


def _write_dormitory_artifacts(
    buildings: list[dict[str, Any]], dataset_dir: Path,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows: list[dict[str, str]] = []
    review_features = []
    for item in buildings:
        props = item["properties"]
        if props.get("category") != "DORMITORY":
            continue
        center = shape(item["geometry"]).representative_point()
        candidate = props.get("dormitoryCandidate") or {}
        row = {
            "osm_id": props["externalId"],
            "current_name": props.get("name", ""),
            "current_category": props.get("category", ""),
            "longitude": f"{center.x:.7f}",
            "latitude": f"{center.y:.7f}",
            "candidate_number": candidate.get("number", ""),
            "candidate_display_name": candidate.get("displayName", ""),
            "confidence": candidate.get("confidence", "UNKNOWN"),
            "evidence": candidate.get("evidence", ""),
            "confirmed_number": "",
            "confirmed_display_name": "",
            "aliases": "",
            "status": "NEEDS_MANUAL_CONFIRMATION",
            "notes": "Engineering matching confidence only; not a factual verification.",
        }
        rows.append(row)
        review_features.append({
            "type": "Feature",
            "id": props["externalId"],
            "geometry": mapping(center),
            "properties": {
                "reviewId": f"dormitory:{props['externalId']}",
                "sourceObjectId": props["externalId"],
                "name": props.get("name", ""),
                "candidateNumber": candidate.get("number", ""),
                "candidateDisplayName": candidate.get("displayName", ""),
                "confidence": candidate.get("confidence", "UNKNOWN"),
                "currentVerificationStatus": props.get("verificationStatus", ""),
                "reason": candidate.get("evidence", ""),
                "severity": "P1" if candidate.get("confidence") == "UNKNOWN" else "P2",
            },
        })
    rows.sort(key=lambda row: (int(row["candidate_number"]) if row["candidate_number"].isdigit() else 999, row["osm_id"]))
    manual_path = dataset_dir / "manual" / "dormitory-review.csv"
    with manual_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DORMITORY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    review = {
        "type": "FeatureCollection",
        "name": "xianlin-dormitory-candidates",
        "metadata": {"developmentOnly": True, "confidenceMeaning": "engineering matching confidence, not factual verification"},
        "features": review_features,
    }
    review_path = dataset_dir / "review" / "dormitory-candidates.geojson"
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows, review


def _complex_report(
    title: str, ids: list[str], buildings_by_id: dict[str, dict[str, Any]], raw_by_id: dict[str, dict[str, Any]],
    local_metric: Callable,
) -> str:
    items = [buildings_by_id[item_id] for item_id in ids]
    lines = [f"### {title}", "", "| OSM ID | Geometry | Centroid (lon, lat) | Area m² | Current tags |", "|---|---|---:|---:|---|"]
    for item in items:
        props = item["properties"]
        geom = shape(item["geometry"])
        center = geom.centroid
        raw_tags = (raw_by_id.get(props["externalId"]) or {}).get("tags", {})
        tags_text = "; ".join(f"{key}={value}" for key, value in sorted(raw_tags.items()))
        lines.append(
            f"| `{props['externalId']}` | {geom.geom_type}, bounds={tuple(round(v, 7) for v in geom.bounds)} | "
            f"{center.x:.7f}, {center.y:.7f} | {local_metric(geom).area:.1f} | {tags_text} |"
        )
    lines += ["", "Pairwise polygon distances:", "", "| A | B | Polygon distance m | Centroid distance m | Touch/intersect |", "|---|---|---:|---:|---|"]
    for index, left in enumerate(items):
        for right in items[index + 1:]:
            left_geom, right_geom = shape(left["geometry"]), shape(right["geometry"])
            lines.append(
                f"| `{left['properties']['externalId']}` | `{right['properties']['externalId']}` | "
                f"{local_metric(left_geom).distance(local_metric(right_geom)):.1f} | "
                f"{local_metric(left_geom.centroid).distance(local_metric(right_geom.centroid)):.1f} | "
                f"{'yes' if left_geom.touches(right_geom) or left_geom.intersects(right_geom) else 'no'} |"
            )
    return "\n".join(lines)


def generate_naming_artifacts(
    layers: dict[str, list[dict[str, Any]]], raw: dict[str, Any], local_metric: Callable,
    dataset_dir: Path,
) -> dict[str, Any]:
    buildings, pois = layers["buildings"], layers["pois"]
    raw_by_id = _raw_index(raw)
    buildings_by_id = {item["properties"]["externalId"]: item for item in buildings}
    issues = _issues(buildings, pois)
    duplicate_buildings = _duplicate_groups(buildings)
    building_display = {item["properties"].get("displayName") or item["properties"].get("name") for item in buildings}
    poi_display = {item["properties"].get("displayName") or item["properties"].get("name") for item in pois}
    duplicate_building_poi = sorted(building_display & poi_display)
    rows, _ = _write_dormitory_artifacts(buildings, dataset_dir)
    issue_counts = {key: len(values) for key, values in issues.items()}
    alias_values = {
        alias for item in buildings + pois for alias in item["properties"].get("aliases", [])
    }
    public_categories = {"LIBRARY", "ADMINISTRATION", "SPORT", "MEDICAL"}
    summary = {
        "totalBuildings": len(buildings),
        "namedBuildings": sum(bool(item["properties"].get("name")) for item in buildings),
        "unnamedBuildings": sum(not item["properties"].get("name") for item in buildings),
        "buildingsWithDisplayName": sum(bool(item["properties"].get("displayName")) for item in buildings),
        "hiddenBuildingLabels": sum(not item["properties"].get("labelVisible", True) for item in buildings),
        "hiddenPoiLabels": sum(not item["properties"].get("labelVisible", True) for item in pois),
        "hiddenTotalLabels": sum(not item["properties"].get("labelVisible", True) for item in buildings + pois),
        "duplicateBuildingNameGroups": len(duplicate_buildings),
        "duplicateBuildingRecords": sum(len(ids) for ids in duplicate_buildings.values()),
        "dormitoryCandidates": len(rows),
        "confirmedDormitoryNumbers": sum(bool(row["confirmed_number"]) for row in rows),
        "teachingBuildings": sum(item["properties"].get("category") == "TEACHING" for item in buildings),
        "canteenBuildings": sum(item["properties"].get("category") == "DINING" for item in buildings),
        "publicBuildings": sum(item["properties"].get("category") in public_categories for item in buildings),
        "buildingPoiDuplicateGroups": len(duplicate_building_poi),
        "linkedPois": sum(bool(item["properties"].get("buildingExternalId")) for item in pois),
        "uniqueAliases": len(alias_values),
        "issueCounts": issue_counts,
    }

    docs_dir = dataset_dir.parents[2] / "docs"
    issue_lines = ["| Classification | Count | Example IDs |", "|---|---:|---|"]
    for key in ISSUE_TYPES:
        values = issues[key]
        issue_lines.append(f"| {key} | {len(values)} | {', '.join(f'`{value}`' for value in values[:5]) or '—'} |")
    duplicate_lines = [f"- **{name}**: {', '.join(f'`{value}`' for value in ids)}" for name, ids in sorted(duplicate_buildings.items())]
    canteen_report = _complex_report(
        "一食堂 three-polygon audit",
        ["osm:way:1390009974", "osm:way:1390009973", "osm:way:1390009975"],
        buildings_by_id, raw_by_id, local_metric,
    )
    admin_report = _complex_report(
        "行政楼 two-polygon audit",
        ["osm:way:223859811", "osm:way:223859826"],
        buildings_by_id, raw_by_id, local_metric,
    )
    audit = f"""# Campus Naming Audit

Generated from the normalized Xianlin dataset on 2026-08-22. `officialName` is source-backed detail text, `displayName` is the short map label, `aliases` are future-search terms, and `keywords` remain search expansion terms. Engineering matching confidence is not factual confidence.

## Statistics

| Metric | Count |
|---|---:|
| Total buildings | {summary['totalBuildings']} |
| Named buildings | {summary['namedBuildings']} |
| Unnamed buildings in normalized layer | {summary['unnamedBuildings']} |
| Buildings with displayName | {summary['buildingsWithDisplayName']} |
| Hidden building labels | {summary['hiddenBuildingLabels']} |
| Hidden POI labels | {summary['hiddenPoiLabels']} |
| Hidden Building + POI labels | {summary['hiddenTotalLabels']} |
| Duplicate building name groups | {summary['duplicateBuildingNameGroups']} |
| Dormitory candidates | {summary['dormitoryCandidates']} |
| Teaching buildings | {summary['teachingBuildings']} |
| Canteen buildings | {summary['canteenBuildings']} |
| Public buildings | {summary['publicBuildings']} |
| Building/POI duplicate groups | {summary['buildingPoiDuplicateGroups']} |
| POIs linked to a building | {summary['linkedPois']} |
| Unique aliases | {summary['uniqueAliases']} |

## Issue classification

{chr(10).join(issue_lines)}

`BUILDING_POI_DUPLICATE` is expected where a physical Building and user-facing POI represent the same place. It is audited, linked through `buildingId`, and should be deduplicated by future search—not deleted here.

## Duplicate Building names

{chr(10).join(duplicate_lines) or '- None'}

{canteen_report}

**Assessment:** all three polygons touch, have identical explicit OSM tags, and form one connected canteen complex. Keep the three physical geometries, produce one POI/label group, and do not auto-merge geometry. The primary POI is linked to `osm:way:1390009974`; all three IDs remain in `relatedBuildingExternalIds`.

{admin_report}

**Assessment:** the polygons are separated (2.8 m) and have materially different footprints, so they are more likely two distinct buildings than one split polygon. Official NJUPT pages confirm the names 行政南楼 and 行政北楼; mapping south/north names to the southern/northern polygons is a spatial inference and remains a field-confirmation item.

## Long and ambiguous institution names

College or department names are retained as POIs when sourced, but do not automatically become formal physical-building names. Labels over 16 characters are hidden until a source-backed short physical name is reviewed; text is never silently truncated into a possibly false name.

## Minimum manual checklist (30 review units)

1. Spot-check dormitory numbers 1–5 against on-building signage.
2. Spot-check 10, 15 and 20 as range anchors.
3. Confirm the special OSM name `21 国防生楼` and whether the public label should remain `21号楼`.
4. Spot-check 22–29 individually (8 items).
5. Spot-check 30, 35 and 40 as range anchors.
6. Spot-check 41–49 individually (9 items).
7. Confirm 青教公寓 has no student-facing numeric building identifier.
8. Confirm southern polygon `osm:way:223859811` is 行政南楼.
9. Confirm northern polygon `osm:way:223859826` is 行政北楼.
10. Confirm the three 一食堂 polygons are one user-facing complex.
11. Confirm 新体育馆 remains the current student-facing name.

The grouped/ranged items above represent 30 concrete review units. If an anchor fails, expand verification to every row in `dormitory-review.csv`; do not infer corrections by sequence.

## Source registry

- NJUPT official service notice confirms 教学1~5号楼, 行政楼, 一/二食堂, 三食堂 and 青教公寓: https://hqjt.njupt.edu.cn/2014/1215/c5002a66724/page.htm
- NJUPT library confirms 仙林校区图书馆: https://lib.njupt.edu.cn/1384/list.htm
- NJUPT service page confirms 仙林一食堂、二食堂、三食堂: https://hqc.njupt.edu.cn/_t311/2014/0905/c5002a66692/page.htm
- NJUPT official pages confirm 行政北楼 and 行政南楼: https://skc.njupt.edu.cn/jgsz/list.htm and https://xkb.njupt.edu.cn/10472/list.htm
- NJUPT official campus pages confirm places including 圆楼、青春剧场、大学生活动中心: https://www.njupt.edu.cn/2024/0705/c72a267415/page.htm and https://www.njupt.edu.cn/2026/0420/c17121a300358/page.htm
"""
    (docs_dir / "CAMPUS_NAMING_AUDIT.md").write_text(audit, encoding="utf-8")

    grouped = defaultdict(list)
    for row in rows:
        grouped[row["confidence"]].append(row)
    sections = []
    for confidence in ("HIGH", "MEDIUM", "LOW", "UNKNOWN"):
        sections += [f"## {confidence} Confidence", "", "| OSM ID | Current Name | Candidate | Evidence |", "|---|---|---|---|"]
        values = grouped[confidence]
        if values:
            for row in values:
                sections.append(f"| `{row['osm_id']}` | {row['current_name']} | {row['candidate_display_name'] or '—'} | {row['evidence']} |")
        else:
            sections.append("| — | — | — | No candidates in this class. |")
        sections.append("")
    dormitory_doc = """# Dormitory Review

All candidates come from explicit OSM names/categories. No building number was inferred from position or neighborhood ordering. `HIGH/MEDIUM/LOW/UNKNOWN` means **engineering matching confidence**, not verified factual confidence. The `confirmed_*` CSV columns are intentionally blank until a human or reliable public source confirms them.

Current result: {total} candidates, {confirmed} confirmed numbers, {pending} pending. Use `?debug=gisp1` and enable **Dormitory Candidates** for map-assisted review.

""".format(total=len(rows), confirmed=summary["confirmedDormitoryNumbers"], pending=len(rows) - summary["confirmedDormitoryNumbers"])
    (docs_dir / "DORMITORY_REVIEW.md").write_text(dormitory_doc + "\n".join(sections), encoding="utf-8")
    return summary
