# Phase 1.5 真实 GIS 数据计划

## Dataset

分层维护 Campus Boundary、Building、Road、Footpath、Green、Water、Sport、Plaza、POI 与可确认的 Building Entrance。真实数据位于 `data/real/xianlin/`，合成测试数据继续保留在 `data/sample-xianlin.geojson`。

## Source Registry

每批来源记录 `source_name`、`source_url`、`source_type`、`license`、`retrieved_at`、`coordinate_system`、`precision`、`verification_status` 和 `notes`。状态使用 RAW、AUTO_VALIDATED、SOURCE_VERIFIED、MANUALLY_REVIEWED、FIELD_VERIFIED、REJECTED；自动 OSM 数据最高只标记 SOURCE_VERIFIED。

## ETL

`fetch_osm_xianlin.py` 以限频、缓存和重试方式获取 Overpass 数据；`xianlin_pipeline.py` 使用 OSM 校界过滤、映射标签、生成稳定 ID、应用名称/高度/POI/别名/入口 manual overrides、分层导出并做几何/范围/重复/道路检查。生产网站不运行 Overpass 请求。

## Tag mapping

- `building=*` → BUILDING（仅保留有名称且在校界审查缓冲区内的 Polygon）
- `highway=footway|path|pedestrian|steps|cycleway|track` → ROAD_PEDESTRIAN
- 其他校内 `highway=*` → ROAD_MAIN
- `leisure=pitch|track|stadium|sports_centre` → SPORT
- `natural=water` / `water=*` → WATER
- `landuse=grass|meadow|forest|recreation_ground` → GREEN
- `amenity=*` / `shop=*` 节点 → POI（必须有名称）

## Stable ID 与更新策略

OSM 对象使用 `osm:<type>:<id>`；由建筑生成的 POI 使用 `osm:<type>:<id>:poi`。后端按 `externalId` upsert，不执行全表清空；启用真实数据时只停用 `data_source=SYNTHETIC` 的展示对象。

## Height 与坐标

OSM `height` 直接记录为 `OSM_HEIGHT`；`building:levels` 按 3.3m/层换算并标记 `ESTIMATED_FROM_LEVELS`；完全未知时数据库保持 NULL，由前端显示 fallback，不伪装成实测高度。全链路为 WGS84 / EPSG:4326，坐标顺序 `[longitude, latitude]`。
