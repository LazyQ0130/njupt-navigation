# NJUPT 智慧校园导航项目计划

## 1. 架构原则

- Monorepo：前端、后端、基础设施和数据规范同仓维护。
- 数据驱动：地点、建筑、入口、路网、场景和配置均来自数据库/API。
- GIS 统一：内部使用 WGS84 / EPSG:4326；任何 GCJ-02、BD-09 数据先经过显式转换层。
- 可演进：Phase 0 使用 GeoJSON，数据规模增长后再引入矢量瓦片。
- 安全默认：公共读取与匿名提交分离；管理写操作认证、限流和审计。

## 2. 系统架构

```text
Mobile/PC Web
  Vue 3 + MapLibre + Pinia
          |
        HTTPS
          |
        Nginx
          |
   Spring Boot REST API
    |        |        |
 PostGIS   Redis*   DeepSeek*
```

`*` Redis 在需要分布式限流/缓存时引入；DeepSeek 仅在 Phase 8 引入且不可成为基础搜索或路由依赖。

## 3. 数据库模型

| 实体 | 关键字段/关系 |
| --- | --- |
| Campus | name、code、boundary、default camera；所有校园数据的根 |
| Building | campus_id、name、aliases、category、Polygon、height/color |
| BuildingEntrance | building_id、Point、步行/骑行/无障碍状态 |
| Poi | campus_id、building_id?、name、aliases、keywords、category、Point |
| PathNode | campus_id、Point |
| PathEdge | source/target、LineString、长度和通行属性 |
| Scenario / ScenarioStop | 数据驱动的新生流程和有序停靠点 |
| MapCorrection | 匿名纠错、对象引用、状态和审核信息 |
| AdminUser | 管理员认证、状态、密码哈希 |
| SystemConfig | 可审计的运行参数 |

Geometry 列固定 SRID 4326，使用 GiST 索引；名称/别名使用 trigram 索引支持中文模糊检索。

## 4. API 规划

### Public

- `GET /api/map/bootstrap`：校园、图层版本、可用数据统计
- `GET /api/map/features`：按校区返回带稳定 ID 和 featureType 的 GeoJSON FeatureCollection
- `GET /api/pois`、`GET /api/pois/search`、`GET /api/pois/{id}`
- `GET /api/buildings/{id}`
- `POST /api/routes`、`POST /api/navigation/reroute`
- `GET /api/scenarios`
- `POST /api/corrections`
- `POST /api/ai/parse`（仅 Phase 8）

### Admin

- `/api/admin/auth/*`
- `/api/admin/pois|buildings|entrances|path-nodes|path-edges`
- `POST /api/admin/imports/geojson`
- `/api/admin/corrections`、`/api/admin/config`、`/api/admin/operation-logs`

统一错误响应包含 code、message、traceId、fieldErrors；所有写请求验证大小、Geometry 与权限。

## 5. 前端模块

- `api`：Axios 实例、DTO 和错误归一化
- `stores`：map、search、route、navigation、anonymousSession
- `views/map`：主地图与移动端布局
- `features/search`：建议、分类和自然语言入口
- `features/routing`：起终点、模式、路线结果
- `features/navigation`：定位、吸附、偏航和演示
- `features/scenarios`：新生数据驱动流程
- `admin`：独立路由和地图编辑工作区

## 6. 后端模块

- `campus`：校园与地图 bootstrap
- `place`：Building、Entrance、Poi 与检索
- `routing`：图构建、A*/Dijkstra、入口选择和指令
- `navigation`：重规划策略与参数
- `scenario`：新生场景
- `correction`：匿名纠错与限流
- `importer`：GeoJSON/未来 OSM、CSV 导入
- `admin`：认证、CRUD 和操作审计
- `ai`：意图解析适配层（Phase 8）

## 7. Phase 0-8

### Phase 0：工程与数据基础

Monorepo、Vue/Spring Boot、PostGIS、Flyway、核心 schema、GeoJSON 导入、示例数据、Docker、测试与数据采集说明。

### Phase 1：2.5D 地图

MapLibre 相机、建筑挤出、基础地表图层、POI、定位/指南针/复位和移动端性能基线。

### Phase 1.5：Real GIS Dataset

在 Phase 2 前建立数据质量门：OSM/官方参考来源登记、分层 GeoJSON、稳定 ID、人工覆盖、Geometry/范围/重复/路网校验、PostGIS 幂等 upsert 和人工审核清单。自动 OSM 数据不能高于 SOURCE_VERIFIED；未现场确认的名称、入口和通行属性继续保持待审核。

### Phase 2：POI 搜索

中文名称/别名/关键词搜索、分类、建议、FlyTo、高亮与 Bottom Sheet。

### Phase 3：路网与规划

入口连接、拓扑检查、步行/骑行限制、A*、距离/时间、GeoJSON 路线和异常覆盖测试。

### Phase 4：GPS 导航

WatchPosition、地图匹配、heading、剩余距离、指令、偏航阈值/防抖/冷却与重规划。

### Phase 5：路线演示

基于路线里程的模拟点、相机跟随、暂停/继续/退出和指令同步。

### Phase 6：新生模式

Scenario/Stop API、报到及校园熟悉流程、快捷入口与可配置内容。

### Phase 7：管理员后台

JWT/BCrypt、CRUD、MapLibre Draw 编辑、合法性校验、撤销/确认、纠错审核与操作日志。

### Phase 8：AI Campus Map

DeepSeek 结构化意图、POI 实体解析、SEARCH/ROUTE/NEARBY/NEW_STUDENT、限流与无 AI 降级。

## 8. 风险与应对

| 风险 | 应对 |
| --- | --- |
| 校园数据不完整或过期 | 来源登记、现场核验、后台编辑、对象 updated_at/version |
| 建筑入口缺失导致穿墙 | 路由目标强制为可用入口，缺失时拒绝或提示 |
| 坐标系混用 | 导入元数据声明、范围检查、转换层与抽样叠图 |
| 道路拓扑断裂 | 导入拓扑报告、孤立节点/连通分量检查、路由测试 |
| 手机渲染压力 | 几何简化、按视野/zoom 加载、避免复杂 3D 资源 |
| 匿名接口滥用 | IP/session 双维度限流、请求体限制与验证码升级路径 |
| AI 幻觉 | LLM 只返回意图，实体必须由数据库解析，路线由 GIS 算法生成 |

## 9. GIS 数据问题

必须为每批数据记录来源、许可、采集日期、坐标系、精度和校验人。OSM 可作为起点，但校园小路、建筑入口、施工/夜间通行信息需要现场核验。官方平面图只作为人工参考，未经许可不得直接再分发其图像或派生受限数据。

## 10. 开发顺序与质量门

每个 Phase 固定执行：需求/数据确认 → schema/API → 实现 → 单元/集成测试 → 前端 lint/build → Docker smoke test → README/TASKS 更新 → 独立提交。上一阶段验收前不进入下一阶段。
