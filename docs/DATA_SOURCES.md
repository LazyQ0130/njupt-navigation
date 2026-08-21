# 地图数据与许可

## Phase 1.5 真实仙林数据

真实 v1 空间 Geometry 来自 OpenStreetMap 2026-08-22 Overpass 提取，校界为 OSM way `89910254`，坐标系 WGS84 / EPSG:4326。数据依据 ODbL 1.0 使用和分发，交互地图必须显示可访问的 **© OpenStreetMap contributors** attribution；完整来源登记见 `data/real/xianlin/metadata/sources.json`。

南京邮电大学官方校区地图、联系地址、校庆跑路线和考试通知只用于登记事实与人工审核提示。仓库没有复制其图片/PDF，也没有从高德、百度、Google 或其他商业地图抓取数据。当前真实数据仅通过自动来源与空间校验，尚未现场核验。

## 当前仓库中的地图内容

`data/sample-xianlin.geojson` 由本项目为 Phase 1 功能验收手工编写。所有坐标、边界、建筑轮廓、建筑名称、道路、绿地、水体、运动场和 POI 都是合成演示内容，不是测绘结果，也不是对南京邮电大学仙林校区真实设施的声明。

- 来源：项目自制合成数据
- 坐标系：WGS84 / EPSG:4326
- 坐标顺序：`[longitude, latitude]`
- 用途：验证 PostGIS、Spring Boot GeoJSON API、MapLibre 2.5D 图层和移动端交互
- 限制：不得用于真实导航、校园管理、应急响应或位置判断

## 地图渲染资源

前端底图是仓库内定义的纯色 MapLibre Style，不请求 Google Maps、高德、百度或其他商业地图瓦片，也不需要商业地图密钥。

MapLibre 的 Symbol Layer 配置了 MapLibre 官方演示字体端点 `https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf`，同时启用浏览器本地 CJK 字形生成。该端点仅用于字体字形，不提供底图或校园数据；网络不可用时，地表、道路和 2.5D 建筑等核心图层仍能渲染，部分文字可能不可见。

界面 attribution 会按当前数据集切换：真实 OSM 数据显示可点击的“© OpenStreetMap contributors · MapLibre”，合成数据则显示 Phase 1 demo 声明；attribution 控件未通过 CSS 隐藏。

## 真实数据人工验收门槛

真实校园数据必须逐批记录来源 URL 或文件、许可、采集日期、原始坐标系、预计精度、转换步骤和已知缺陷；人工核验时还应登记核验人。不得复制或分发未经授权的商业地图瓦片、官方平面图或受保护的派生数据。

真实数据至少需要人工叠图和现场抽样核验：校区边界、建筑 Polygon/高度/正式名称、校门与建筑入口、主路与步行道路、绿地/水体/运动场、坐标整体偏移和数据时效性。
