# 南邮仙林 2.5D 智慧校园导航系统

面向南京邮电大学仙林校区学生和访客的移动端优先校园地图与导航平台。本仓库当前进入 **Phase 1.6：真实 GIS 人工核验辅助与拓扑清理**；搜索、路由、导航及后台编辑器将在后续阶段按顺序实现。

## 产品目标

- 建立可维护的校园 GIS 数据库，而不是把地点坐标硬编码在前端。
- 支持建筑入口级步行/骑行路由，避免路线穿墙。
- 普通学生免登录，管理员操作受保护并可审计。
- 以手机竖屏体验和中端移动设备性能为优先。

## 系统架构

```text
Browser (Vue 3)
  -> Nginx /api reverse proxy
  -> Spring Boot REST API
  -> PostgreSQL + PostGIS
```

Phase 1 提供：MapLibre 全屏地图、数据库驱动的建筑挤出与地表/道路/POI 图层、建筑交互、定位/指南针/复位、公开 GeoJSON API、移动端布局和合成演示数据。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、MapLibre GL JS、Turf.js、Tailwind CSS、Pinia、Vue Router、Axios
- 后端：Java 21、Spring Boot 3、Spring Data JPA、Spring Security、Flyway、JTS/Hibernate Spatial
- 数据：PostgreSQL 16、PostGIS 3.4，内部统一 EPSG:4326
- 部署：Docker Compose、Nginx

## 目录结构

```text
frontend/                 Vue + MapLibre 学生端地图
backend/                  Spring Boot 地图 API 与 GIS 导入
infra/nginx/              反向代理配置
data/                     可提交的示例 GIS 数据
docs/                     数据采集与架构说明
PROJECT_PLAN.md           完整 Phase 0-8 规划
TASKS.md                  阶段 Checklist
docker-compose.yml        本地完整环境
```

## 本地启动

### Docker（推荐）

```powershell
Copy-Item .env.example .env
# 修改 .env 中的密码后启动
docker compose up --build
```

访问：

- Web：<http://localhost>
- 后端健康检查：<http://localhost/api/actuator/health>
- PostgreSQL：`localhost:5432`

### 分开开发

先启动数据库：

```powershell
Copy-Item .env.example .env
docker compose up -d postgres
```

后端：

```powershell
Set-Location backend
mvn spring-boot:run
```

前端：

```powershell
Set-Location frontend
npm install
npm run dev
```

Vite 会把 `/api` 代理到 `http://localhost:8080`。

## 环境变量

`.env.example` 只提供占位值。真实 `.env`、数据库密码、JWT Secret 和未来的 DeepSeek Key 均不会提交到 Git。

| 变量 | 用途 |
| --- | --- |
| `DB_HOST/DB_PORT/DB_NAME` | 后端数据库连接 |
| `DB_USER/DB_PASSWORD` | 数据库凭据 |
| `ADMIN_BOOTSTRAP_USER/PASSWORD` | Phase 0 导入端点临时 Basic Auth；Phase 7 将替换为正式管理员体系 |
| `GEOJSON_IMPORT_FILE` | 可选：后端启动时导入容器内 GeoJSON 文件 |
| `GEOJSON_IMPORT_DIRECTORY` | 可选：后端启动时按依赖顺序导入分层真实 GeoJSON 目录 |
| `GEOJSON_IMPORT_DATASET_MODE` | 启动导入完成后激活 `demo` 或 `real` 数据集 |

## 数据库初始化

Flyway 在后端启动时自动执行 `backend/src/main/resources/db/migration`。首个迁移会：

1. 启用 `postgis` 与 `pg_trgm`；
2. 创建 campus、building、entrance、poi、path_node、path_edge、scenario 等表；
3. 为 Geometry、别名搜索和路网字段建立索引；
4. 插入校区元数据；Docker 开发环境会幂等导入仓库内的真实仙林分层 GeoJSON。

## GeoJSON 导入

示例文件位于 `data/sample-xianlin.geojson`。支持 `FeatureCollection` 中的：

- `Polygon` / `MultiPolygon` + `featureType=BUILDING`
- `Point` + `featureType=POI`
- `Polygon` / `MultiPolygon` + `featureType=CAMPUS_BOUNDARY|GREEN|WATER|SPORT|PLAZA`
- `LineString` / `MultiLineString` + `featureType=ROAD_MAIN|ROAD_PEDESTRIAN`

通过受保护端点导入：

```powershell
curl.exe -u "admin:change-me-now" -F "file=@data/sample-xianlin.geojson" http://localhost:8080/api/admin/imports/geojson
```

响应包含成功数、失败数以及逐条错误原因。示例文件只用于手工测试，不再由 Docker Compose 默认加载。生产环境使用前必须修改临时管理员密码。

## 真实仙林 GIS 数据

`data/real/xianlin/` 保存按 campus/buildings/roads/surfaces/pois/entrances 分层的 OSM 派生 v1，原始提取保存在 `data/raw/osm/`。数据采用 ODbL 1.0，需显示 `© OpenStreetMap contributors`；南邮官方网页仅作来源登记和人工核验参考，未复制其图片或商业地图数据。

```powershell
python -m pip install -r scripts/gis/requirements.txt
python scripts/gis/fetch_osm_xianlin.py
python scripts/gis/xianlin_pipeline.py build
docker compose up -d --build
```

Pipeline 先运行 Geometry/坐标/校界/重复/道路和命名检查；Docker Compose 随后按 campus/surfaces/buildings/pois/roads/entrances 的依赖顺序幂等 upsert，并激活 `real` 数据集，只停用 `data_source=SYNTHETIC` 的展示对象。分开开发或需要手工刷新时仍可运行 `./scripts/import-real-xianlin.ps1`。生产使用 `prod` profile 时启动 importer 被禁用。当前覆盖 87 建筑、36 POI、181 条道路/步道、193 个地表/运动/水体对象和 1 个校界；入口为 0。一食堂三个相接建筑 Polygon 保持独立，但只派生一个用户侧 POI。

Phase 1.6 增加只读 review GeoJSON、道路端点分类、道路穿建筑解释、入口候选、人工 override/manifest 和现场 CSV 工作流。开发环境可用 `?debug=gisp1` 开启只读 GIS Review Mode；普通构建及学生 UI 默认隐藏。当前 368 个道路端点中 271 个已连接、97 个待分级复核（P0 2 / P1 25 / P2 70），并生成 5 个入口候选但没有将其冒充正式入口。详见 `docs/ROAD_TOPOLOGY_REVIEW.md`、`docs/FIELD_REVIEW_ROUTES.md` 和 `docs/GIS_VALIDATION_REPORT.md`。

Phase 1.6.2 以 Flyway V5 增加兼容式 `official_name`、`display_name` 和 `label_visible`，保留 `name`；API 同时输出别名和 Building/POI 关联。地图标签使用 `displayName ?? name`，无意义标签被抑制，宿舍编号仅在 zoom 17+ 显示。50 个宿舍候选全部来自显式 OSM 名称/分类，`confirmed_*` 仍为空；开发审核层和人工 CSV 详见 `docs/CAMPUS_NAMING_AUDIT.md` 与 `docs/DORMITORY_REVIEW.md`。

## Phase 1 地图 API

- `GET /api/map/bootstrap`：校区相机、浏览边界、统计和图层可用性。
- `GET /api/map/features?campusCode=NJUPT_XIANLIN`：标准 GeoJSON `FeatureCollection`；每个 Feature 都包含稳定 `id` 和 `properties.featureType`，Building/POI 还可包含 `officialName`、`displayName`、`aliases`、`labelVisible`，POI 可包含 `buildingId`。

前端使用不依赖商业密钥的纯色底图样式。地图内容全部来自 PostGIS → Spring Boot → GeoJSON → MapLibre 数据链。Docker 默认显示 OSM 派生数据并保留 OSM attribution；示例文件中的合成名称、坐标和形状仅供测试，不能用于真实导航。详见 `docs/DATA_SOURCES.md`。

## 管理员账号初始化

Phase 0 仅为 GeoJSON 导入接口提供环境变量驱动的 HTTP Basic 临时保护，不写入数据库。正式 JWT、BCrypt、管理员管理和操作日志 UI 属于 Phase 7。

## 验证命令

```powershell
Set-Location frontend
npm run lint
npm run test
npm run build

Set-Location ../backend
mvn test

Set-Location ..
docker compose config
```

## Phase 开发进度

- [x] Phase 0：工程、PostGIS 模型、迁移、示例数据、导入、Docker
- [x] Phase 1：2.5D 校园地图（合成数据验收）
- [x] Phase 1.5：真实仙林 GIS v1（自动采集、校验、导入）
- [ ] Phase 1.6：人工核验辅助、拓扑清理与入口 v1（工具完成，等待 P0/现场核验）
- [x] Phase 1.6.2：命名审计、宿舍候选工作流与标签层级
- [ ] Phase 2：POI 搜索
- [ ] Phase 3：校园路网与路线规划
- [ ] Phase 4：GPS 导航
- [ ] Phase 5：路线演示
- [ ] Phase 6：新生模式
- [ ] Phase 7：管理员地图编辑后台
- [ ] Phase 8：AI 自然语言意图解析

## 后续规划

Phase 2 将在现有地图上实现 POI 中文名称、别名与关键词搜索、分类建议、FlyTo 和结果高亮。进入任何真实导航验收前，仍需采集并人工核验真实的校园边界、建筑 Polygon、高度、入口和道路数据。

许可、attribution 和第三方数据来源已记录于 `docs/DATA_SOURCES.md` 与真实数据 source registry。禁止提交或分发未经授权的商业地图瓦片与受保护数据。
