# 仙林真实 GIS v1 自动校验报告

生成日期：2026-08-22；数据集：`njupt-xianlin-real-v1`。

## 结果

- 正式输出：500；Geometry error：0；坐标范围错误：0；校界缓冲区外：0；PostGIS SRID 全部为 4326
- Building：87；POI：38；Road main：120；Footpath：61
- Green：176；Sport：13；Water：4；Campus boundary：1；Entrance：0
- 75 栋建筑具有 OSM `height` 或 `building:levels` 高度依据；12 栋未知并保持 NULL
- 原始数据排除：69 个校界外/无效建筑、35 个无名称建筑、3 条非简单道路
- 自动 warning：338，主要来自未命名道路/地表、重复名称和路网人工复核项

## 路网质量

当前 181 条展示道路产生 368 个端点，其中 244 个端点在 4m 阈值内没有连接。它们不是可路由 PathEdge，不能用于导航。检测到 3 条道路与建筑内部相交：`osm:way:224954286`、`osm:way:970894656`、`osm:way:224941322`；仅记录 warning，未自动删除。

## 解释

报告证明数据通过自动格式、坐标、Geometry 和校界范围门槛，不代表位置已现场核验。全部 OSM 对象当前最高为 `SOURCE_VERIFIED`，没有对象被标记为 `MANUALLY_REVIEWED` 或 `FIELD_VERIFIED`。
