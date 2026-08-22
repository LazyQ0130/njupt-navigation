# Map Rendering Debug Report

## Symptoms

`http://localhost` 和 Vite 开发页都能显示搜索框、地图控件、attribution 和有正常尺寸的 MapLibre canvas，但地图区域只有 `#F3F1EC` 背景，校园建筑、道路和地表全部不可见。该现象属于 UI 存在、canvas 存在、但自有 GeoJSON 图层不可见（B/C/E），不是页面完全空白。

## Root cause

根因在 MapLibre GeoJSON Web Worker 的构建与部署链路：

1. MapLibre GL JS 6 默认根据主模块的 `import.meta.url` 寻找相邻的 `maplibre-gl-worker.mjs`，Vite 的依赖优化和生产构建没有自动发布这个相邻文件，导致 `campus-features` 永远停留在 loading。
2. 简单使用 `?url` 只能复制 Worker 入口。该入口仍引用 `maplibre-gl-shared.mjs`，生产镜像中没有这一依赖，Nginx 日志显示请求返回 404。最终使用 Vite 的 `?worker&url` 打包完整 Worker 依赖图。
3. Alpine Nginx 默认把 `.mjs` 返回为 `application/octet-stream`。配置中显式声明 JavaScript MIME，避免后续模块 Worker 再次被浏览器拒绝。

另有一个独立的启动数据问题：Docker Compose 原先每次启动都导入 `sample-xianlin.geojson`，会重新启用合成数据并覆盖真实校区 camera/bounds。Compose 现按固定顺序导入 `data/real/xianlin` 的六个分层文件并激活 `real` 数据集。

Camera、CSS、WebGL、FeatureType 与 Geometry 均不是主因。真实校界、真实 camera/bounds、500 个 API Feature 和全部 10 个视觉图层存在时，Worker 修复前仍然是 0 个 source/rendered feature；Worker 修复后立即出现要素。

## Evidence

修复前（真实 Edge、Vite，真实数据已启用）：

- `/api/map/bootstrap` 与 `/api/map/features` 均为 200；API Feature 为 500。
- `CAMPUS_BOUNDARY=1`、`BUILDING=87`、`ROAD_MAIN=120`、`ROAD_PEDESTRIAN=61`、`GREEN=176`、`WATER=4`、`SPORT=13`、`POI=38`。
- 校界为 OSM way `89910254`；抽样建筑为合法 WGS84 `MultiPolygon`，坐标顺序为 longitude/latitude。
- map host 与 canvas 为 `1699 × 935`；10 个视觉图层全部存在。
- `sourceLoaded=false`、`querySourceFeatures=0`、`queryRenderedFeatures=0`。
- Vite 依赖目录缺少 MapLibre Worker；中间生产构建进一步记录到 `GET /assets/maplibre-gl-shared.mjs 404`。

修复后（真实 Edge、Vite）：

- `sourceLoaded=true`、`querySourceFeatures=1114`、`queryRenderedFeatures=717`。`querySourceFeatures`/`queryRenderedFeatures` 会包含分块和跨图层重复项，因此不会等于 API 的 500。
- 当前视口渲染类型：`BUILDING=211`、`ROAD_MAIN=262`、`ROAD_PEDESTRIAN=56`、`GREEN=137`、`SPORT=14`、`WATER=1`、`CAMPUS_BOUNDARY=16`、`POI=20`。
- `building-extrusion` 图层查询到 71 项；真实 Edge 截图可见建筑高度、侧面和阴影。
- Compose 生产构建输出单文件 `maplibre-gl-worker-*.js`，不再请求缺失的 shared module。

## Fix

- 用 `maplibre-gl-worker.mjs?worker&url` 显式设置 MapLibre Worker URL。
- 为 Nginx 增加 `.mjs` JavaScript MIME 兜底。
- 从真实 `CAMPUS_BOUNDARY` 计算 bbox/center；首次加载与“返回校园”均按真实边界 `fitBounds`，保存的 camera/bounds 仅作 fallback。
- 地图创建后在 animation frame 再执行 `resize` 与 `fitBounds`。
- 开发环境暴露轻量诊断：API/source/rendered 数量、类型、图层、相机与 canvas 尺寸；只有 source 已完成且 API 非空、渲染仍为 0 时才报警。
- Docker 启动时幂等导入真实分层 GIS 并激活 real 模式。

当前样式仍是无商业底图的自绘校园图，不是高德、百度或 Apple Maps 城市底图。本次没有接入新的 basemap。

## Regression tests

- `campusViewport.test.ts`：真实仙林校界 bbox/center、保存视野 fallback、移动端/桌面 padding。
- `mapConfig.test.ts`：真实边界视野覆盖旧 camera；MapLibre Worker 使用显式 Vite bundle URL。
- `renderDiagnostics.test.ts`：FeatureType 统计不会静默丢弃已规范化数据。
- 前端：`npm run lint`、`npm run test`、`npm run build`。
- 后端：`mvn verify`。
- 完整栈：`docker compose up -d --build`，检查六个真实分层文件导入、500 个 OPENSTREETMAP Feature 与 Worker 请求。

## Manual validation steps

1. 运行 `docker compose up -d --build`。
2. 打开普通桌面 Chrome 或 Edge 的 `http://localhost`，必要时硬刷新一次以清除旧 bundle 缓存。
3. 肉眼确认校界、建筑、建筑高度、主路/步道、绿地、水体/运动场和 POI 点。
4. 拖动、缩放、旋转地图，再点击“返回校园默认视角”，确认重新 fit 到完整真实校界。
5. 开发模式打开 Vite URL，在 console 查看 `[NJUPT Map] render diagnostics`，确认 `sourceLoaded=true` 且 `renderedFeatureCount>0`。
6. 如再次出现纯色背景，先检查 Worker 及其依赖是否均为 200、JavaScript MIME 是否正确，再检查诊断中的 source/rendered 差异。
