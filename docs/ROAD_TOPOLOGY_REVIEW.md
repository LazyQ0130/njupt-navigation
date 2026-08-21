# 仙林校区 Road Topology Review

本报告由 `scripts/gis/xianlin_pipeline.py build` 生成的数据汇总而来。阈值为：共享拓扑 0.15m、P0 gap 2m、near road 4m、near building 5m、near campus boundary 10m。分类是审核候选，不是人工事实。

## 从 244 到可审核工作集

旧版“244 disconnected endpoints”只比较道路端点之间的距离，因此把接入另一条道路中段的 T 型连接也算成断点。v2 对其他道路的完整 LineString 求距：

- 总端点 368；实际已连接 271；进入审核层 97。
- 旧 244 中有 163 个已连接道路中段；其余 81 个分为正常末端 58、近建筑 6、近校界 3、近其他道路 5、孤立段 9。
- v2 另发现 16 个旧算法漏掉的未共享拓扑端点：它们虽靠近另一个端点，但并没有真正连到其他 Road Geometry。

最终 97 个审核端点：`LIKELY_TOPOLOGY_GAP` 2、`LIKELY_VALID_TERMINUS` 66、`NEAR_BUILDING_ENTRANCE` 6、`NEAR_CAMPUS_BOUNDARY` 3、`NEAR_OTHER_ROAD` 11、`ISOLATED_SEGMENT` 9、`AMBIGUOUS` 0；优先级 P0 2、P1 25、P2 70。

## P0 topology gaps

两个 P0 是同一处相向缺口，涉及 2 条道路：

| Endpoint | 目标道路 | 距离 | 建议 |
| --- | --- | ---: | --- |
| `osm:way:223699479:0:end` | `osm:way:964850646`（仙境路） | 0.79m | `MERGE_ENDPOINT` candidate |
| `osm:way:964850646:1:start` | `osm:way:223699479` | 1.56m | `MERGE_ENDPOINT` candidate |

两条候选连接线未穿已知建筑/水体，且道路语义兼容；但 `suggestedFix.applied=false`。人工确认后才可写入 `manual/road-overrides.geojson`，禁止批量 snap。

## Road / building intersections

| Road | Building | 长度 / 面积 | 暂定类别 | 建议 |
| --- | --- | ---: | --- | --- |
| `osm:way:224954286` | `osm:way:224990427` 连廊 | 4.30m / 0m² | C/D | 保留道路，核验是否为室内、建筑下方或架空通道 |
| `osm:way:224954286` | `osm:way:224990428` 连廊 | 4.31m / 0m² | C/D | 同上；现场确认两个连廊 Polygon 的层级 |
| `osm:way:970894656` | `osm:way:223699451` 教1 | 55.14m / 0m² | C/D | OSM 有 covered/tunnel 语义，保留并核验层级/入口 |
| `osm:way:224941322` | `osm:way:223859827` 主席台 | 4.14m / 0m² | A/B | P0；对照现场判断道路偏移或建筑 Polygon 过大 |

道路是 LineString，因此相交面积为 0；完整相交 Geometry 位于 `review/road-building-intersections.geojson`。没有因相交而自动裁掉任何道路。

## 审核与修复规则

- P0：明显影响主路径或无法解释的穿建筑问题；本批端点 2 个，intersection 1 个。
- P1：近建筑、近其他道路、候选入口或可解释但需确认的相交。
- P2：更可能为正常末端/边界末端，抽查即可。
- 自动过程只输出 `suggestedFix`，且固定 `applied=false`。
- `REPLACE_GEOMETRY`、`DISABLE_SOURCE_OBJECT`、`ADD_MANUAL_PATH`、`MERGE_ENDPOINT` 只能通过带审核元数据的 `manual/road-overrides.geojson` 应用；raw OSM 永不改写。
