# Campus Naming Audit

Generated from the normalized Xianlin dataset on 2026-08-22. `officialName` is source-backed detail text, `displayName` is the short map label, `aliases` are future-search terms, and `keywords` remain search expansion terms. Engineering matching confidence is not factual confidence.

## Statistics

| Metric | Count |
|---|---:|
| Total buildings | 87 |
| Named buildings | 87 |
| Unnamed buildings in normalized layer | 0 |
| Buildings with displayName | 87 |
| Hidden building labels | 18 |
| Hidden POI labels | 2 |
| Hidden Building + POI labels | 20 |
| Duplicate building name groups | 5 |
| Dormitory candidates | 50 |
| Teaching buildings | 9 |
| Canteen buildings | 5 |
| Public buildings | 5 |
| Building/POI duplicate groups | 17 |
| POIs linked to a building | 23 |
| Unique aliases | 124 |

## Issue classification

| Classification | Count | Example IDs |
|---|---:|---|
| UNNAMED | 0 | — |
| GENERIC_NAME | 8 | `osm:way:224938858`, `osm:way:224938894`, `osm:way:224990427`, `osm:way:224990428`, `osm:way:223859827` |
| DUPLICATE_NAME | 13 | `osm:way:223859811`, `osm:way:223859826`, `osm:way:224938858`, `osm:way:224938894`, `osm:way:1390009974` |
| OVERLONG_NAME | 4 | `osm:way:1173057050`, `osm:way:1173057055`, `osm:way:1173057050:poi`, `osm:way:1173057055:poi` |
| AMBIGUOUS_NAME | 8 | `osm:way:1173057051`, `osm:way:1173057050`, `osm:way:1173057055`, `osm:way:1173059720`, `osm:way:1173057051:poi` |
| TECHNICAL_NAME | 0 | — |
| MISSING_DISPLAY_NAME | 0 | — |
| MISSING_ALIAS | 47 | `osm:way:224938858`, `osm:way:224938894`, `osm:way:1173057051`, `osm:way:224954737`, `osm:way:224990427` |
| DORMITORY_UNKNOWN_NUMBER | 1 | `osm:way:225265337` |
| BUILDING_POI_DUPLICATE | 36 | `osm:way:1173057050`, `osm:way:1173057050:poi`, `osm:way:1173057051`, `osm:way:1173057051:poi`, `osm:way:1173057053` |

`BUILDING_POI_DUPLICATE` is expected where a physical Building and user-facing POI represent the same place. It is audited, linked through `buildingId`, and should be deduplicated by future search—not deleted here.

## Duplicate Building names

- **主席台**: `osm:way:223859827`, `osm:way:224940881`
- **南邮仙林一食堂**: `osm:way:1390009974`, `osm:way:1390009973`, `osm:way:1390009975`
- **行政楼办公楼**: `osm:way:223859811`, `osm:way:223859826`
- **连廊**: `osm:way:224990427`, `osm:way:224990428`
- **门卫**: `osm:way:224938858`, `osm:way:224938894`, `osm:way:225109136`, `osm:way:223859807`

### 一食堂 three-polygon audit

| OSM ID | Geometry | Centroid (lon, lat) | Area m² | Current tags |
|---|---|---:|---:|---|
| `osm:way:1390009974` | Polygon, bounds=(118.9281097, 32.1105686, 118.9284938, 32.1110082) | 118.9282829, 32.1108409 | 783.6 | amenity=restaurant; building=yes; building:levels=3; fast_food=cafeteria; name=南邮仙林一食堂; name:zh=南邮仙林一食堂 |
| `osm:way:1390009973` | Polygon, bounds=(118.9283051, 32.1102378, 118.9287588, 32.1105691) | 118.9285601, 32.1104271 | 1145.5 | amenity=restaurant; building=yes; building:levels=3; fast_food=cafeteria; name=南邮仙林一食堂; name:zh=南邮仙林一食堂 |
| `osm:way:1390009975` | Polygon, bounds=(118.9283223, 32.1105686, 118.9287943, 32.1109954) | 118.9285682, 32.1107615 | 1635.8 | amenity=restaurant; building=yes; building:levels=3; fast_food=cafeteria; name=南邮仙林一食堂; name:zh=南邮仙林一食堂 |

Pairwise polygon distances:

| A | B | Polygon distance m | Centroid distance m | Touch/intersect |
|---|---|---:|---:|---|
| `osm:way:1390009974` | `osm:way:1390009973` | 0.0 | 52.7 | yes |
| `osm:way:1390009974` | `osm:way:1390009975` | 0.0 | 28.3 | yes |
| `osm:way:1390009973` | `osm:way:1390009975` | 0.0 | 37.0 | yes |

**Assessment:** all three polygons touch, have identical explicit OSM tags, and form one connected canteen complex. Keep the three physical geometries, produce one POI/label group, and do not auto-merge geometry. The primary POI is linked to `osm:way:1390009974`; all three IDs remain in `relatedBuildingExternalIds`.

### 行政楼 two-polygon audit

| OSM ID | Geometry | Centroid (lon, lat) | Area m² | Current tags |
|---|---|---:|---:|---|
| `osm:way:223859811` | Polygon, bounds=(118.9237431, 32.1077912, 118.9245952, 32.1080277) | 118.9241661, 32.1079278 | 1735.4 | building=yes; building:levels=6; name=行政楼办公楼; name:zh=行政楼办公楼 |
| `osm:way:223859826` | Polygon, bounds=(118.9241143, 32.1080513, 118.9252364, 32.1085024) | 118.9246221, 32.1083169 | 3754.2 | building=yes; building:levels=6; name=行政楼办公楼; name:zh=行政楼办公楼 |

Pairwise polygon distances:

| A | B | Polygon distance m | Centroid distance m | Touch/intersect |
|---|---|---:|---:|---|
| `osm:way:223859811` | `osm:way:223859826` | 2.8 | 60.8 | no |

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
