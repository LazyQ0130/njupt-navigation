# 仙林校区真实 GIS Validation Report v2

生成日期：2026-08-22；数据集：`njupt-xianlin-real-v1`；坐标系：WGS84 / EPSG:4326。

## 基础校验

- 正式输出 498 个对象：Building 87、POI 36、Road 120、Footpath 61、Green 176、Sport 13、Water 4、Campus boundary 1、Entrance 0。POI 减少 2 是一食堂三个相接 Polygon 改为一个用户侧 POI，不是删除 Building Geometry。
- Geometry error 0、坐标范围错误 0、校界缓冲区外 0、重复稳定 ID 0；PostGIS SRID 全部为 4326。
- 75 栋建筑具有 OSM `height` 或 `building:levels` 高度依据；12 栋未知并保持 NULL。
- 原始数据排除 69 个校界外/无效建筑、35 个无名称建筑和 3 条非简单道路。
- 自动 warning 338，主要为未命名对象、重复名称及需人工解释的路网项。warning 数量不是质量评分，也不是清零目标。

## Topology classification

181 条展示道路共有 368 个端点。按“端点到其他道路完整 Geometry”的距离重新分析后，271 个已实际接入道路，97 个进入人工审核层：

| 分类 | 数量 | 说明 |
| --- | ---: | --- |
| `LIKELY_TOPOLOGY_GAP` | 2 | 小于 2m、语义兼容且候选连接不穿已知障碍 |
| `LIKELY_VALID_TERMINUS` | 66 | 更可能为正常支路/广场/设施末端，仍只是机器分类 |
| `NEAR_BUILDING_ENTRANCE` | 6 | 距建筑边界不超过 5m，不自动作为入口 |
| `NEAR_CAMPUS_BOUNDARY` | 3 | 距校界不超过 10m，可能正常延伸至校外 |
| `NEAR_OTHER_ROAD` | 11 | 距其他道路 2–4m，需判断是否应连接 |
| `ISOLATED_SEGMENT` | 9 | 位于只有 1–2 条 edge 的小连通分量 |
| `AMBIGUOUS` | 0 | 当前规则未产生无法归类项 |

优先级为 P0 2、P1 25、P2 70。未解决 P0 是 `osm:way:223699479` 与 `osm:way:964850646` 的两个相向断点；所有 `suggestedFix` 均为 `applied=false`。

旧报告的 244 个“4m 内无其他端点”使用的是 endpoint-to-endpoint 启发式，不等于 244 个断路。v2 中，163 个已确认接入另一道路的中段；旧集合剩余 81 个（正常末端 58、近建筑 6、近校界 3、近其他道路 5、孤立段 9），另发现 16 个旧启发式因靠近其他端点而漏掉、但并未真正共享拓扑的端点。详见 `ROAD_TOPOLOGY_REVIEW.md`。

## Building intersection analysis

共 3 条道路、4 个 road/building 组合：

- `osm:way:224954286` 分别穿过两个名为“连廊”的 Polygon 4.30m、4.31m。暂归 C/D（室内、建筑下方或架空通道）候选，P1，保留道路并现场确认。
- `osm:way:970894656` 与“教1”相交 55.14m，OSM 标记含 covered/tunnel 语义。暂归 C/D，P1，保留并核验通道层级。
- `osm:way:224941322` 与“主席台”相交 4.14m，无足够标签解释。暂归 A/B（道路 Geometry 或建筑 Polygon 需要修正），P0，必须叠图/现场确认。

相交面积因道路是 LineString 均为 0；报告保留原 Geometry 和建议，不自动裁切道路或建筑。

## Entrance 与人工覆盖

- 正式 Entrance：0；拥有正式入口的核心建筑：0/18。
- 工程候选入口：5，关联教5（2 个）、25、行政楼办公楼、收发室；全部仍为 `PENDING_REVIEW`，access 字段为 NULL，不进入 Entrance 表。
- 核心建筑人工核验：0/18；核心 POI 人工核验：0/20。
- Campus Boundary、南/北门、核心建筑名称、宿舍与食堂仍为 `PENDING_MANUAL_IDENTIFICATION` 或 `SOURCE_VERIFIED`，没有对象被虚假提升为 `MANUALLY_REVIEWED` / `FIELD_VERIFIED`。

## Naming quality

- 87/87 个 Building 已生成 `displayName`；其中 18 个 generic、学院/教学部占位名、超长名或重复次要 Polygon 的学生端标签被隐藏，Geometry 仍保留。学院仍可作为 POI；仅 2 个超长学院 POI 标签被隐藏，共 20 个无意义或待核验标签不进入学生端。
- 50 个宿舍候选中 49 个带显式数字 OSM 名称，1 个为青教公寓；已确认编号仍为 0。`HIGH` 只表示工程匹配规则明确，不表示人工事实核验。
- 原始 Building 同名 5 组（13 个记录）；Building/POI 同语义 17 组。23 个 POI 已通过显式派生或唯一 point-in-polygon 关系关联 Building。
- 一食堂三个 Polygon 两两接触且 OSM tags 相同，判断为同一 connected complex；未合并 Geometry，主 Building + 相关 Building ID 共同支撑一个 POI。
- 两个原“行政楼办公楼” Polygon 相距 2.8m，更像两栋独立楼；行政南楼/北楼名称由校方页面与南北空间匹配得出，仍需现场确认。

完整分类、距离、centroid、原始 tags 与来源见 `CAMPUS_NAMING_AUDIT.md`。

## 结论

数据继续通过格式、Geometry、范围和稳定 ID 门槛，但人工质量门尚未通过。当前最小人工工作集是 2 个 P0 拓扑端点、1 个 P0 道路穿建筑组合，以及现场路线中列出的核心名称、校门和入口。完成核验前，本数据不能作为真实导航路网。
