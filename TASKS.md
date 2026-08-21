# 项目任务清单

## Phase 0 — 工程与地图数据基础

- [x] 检查工作目录与工具链
- [x] 建立 monorepo 结构和安全 `.gitignore`
- [x] 初始化 Vue 3 + TypeScript + Vite 前端
- [x] 初始化 Spring Boot 3 + Java 21 后端
- [x] 配置 PostgreSQL + PostGIS
- [x] 创建 Flyway 数据库迁移
- [x] 建立 Campus / Building / Entrance / POI / Path / Scenario 等 schema
- [x] 实现地图 bootstrap API
- [x] 实现 GeoJSON 校验与导入服务/API
- [x] 添加测试 GeoJSON 和初始示例数据
- [x] 编写地图数据采集说明
- [x] 配置 Docker Compose、Nginx、healthcheck、volume 和 restart policy
- [x] 执行全栈 Docker smoke test（PostGIS、迁移、前后端、Nginx、导入与幂等更新）
- [x] 运行后端测试、前端测试/lint/build 与 Compose 配置检查

## Phase 1 — 2.5D 校园地图

- [x] 引入 MapLibre GL JS 与 Turf.js
- [x] 相机、地图边界与图层可用性由 bootstrap API 驱动
- [x] 建筑 Polygon 与数据库高度/底高/颜色驱动的 fill-extrusion
- [x] 校区边界、道路、草坪、水体、操场、广场图层
- [x] POI Symbol/Circle 与建筑点击高亮
- [x] 定位、越界提示、指南针、Reset View
- [x] 100dvh、安全区、键盘焦点、移动端与桌面响应式布局
- [x] 加载失败、无数据、地图资源错误与定位错误状态
- [x] 前端 mapper/config/state/control 测试和后端 GeoJSON/API 测试
- [x] 合成数据全栈验收与来源声明
- [ ] 真实仙林校区边界、建筑、道路和 POI 的授权采集与现场核验

## Phase 1.5 — 真实仙林 GIS 数据质量门

- [x] OSM Overpass 获取脚本、缓存与 ODbL attribution
- [x] 南邮官方公开参考来源登记（不分发图片/PDF）
- [x] 分层真实 GeoJSON、稳定 ID 和 manual override 目录
- [x] Geometry、坐标、校界、重复、路网连接和穿建筑校验
- [x] V3 来源/核验元数据与未知高度 NULL 语义
- [x] Building/POI/MapFeature/Entrance 幂等导入链路
- [x] Demo/Real 来源级切换与 production Demo 启动保护
- [x] Validation report 与人工审核 checklist
- [ ] 校界、名称、食堂/宿舍/校门和道路人工叠图核验
- [ ] 主要建筑入口与通行属性现场核验
- [ ] 将确认对象提升为 MANUALLY_REVIEWED / FIELD_VERIFIED

## Phase 2 — POI 搜索

- [ ] 中文名称/别名/关键词模糊搜索
- [ ] 分类筛选与搜索建议
- [ ] FlyTo、建筑高亮、Bottom Sheet
- [ ] `教2` 等别名验收用例

## Phase 3 — 路网与路线规划

- [ ] 路网导入与拓扑校验
- [ ] 建筑入口选择
- [ ] 步行/骑行 A* 路由
- [ ] 距离、时间、Geometry、导航指令
- [ ] 禁行、断路、最短路和不穿墙测试

## Phase 4 — GPS 导航

- [ ] Geolocation / WatchPosition 状态处理
- [ ] 最大距离约束的 Map Matching
- [ ] 相机跟随和 heading
- [ ] 偏航阈值、防抖、冷却和重规划

## Phase 5 — 路线演示

- [ ] 模拟点沿路线移动
- [ ] 相机与指令同步
- [ ] 暂停、继续、退出

## Phase 6 — 新生模式

- [ ] Scenario / ScenarioStop API
- [ ] 新生报到与校园熟悉流程
- [ ] 教学楼/宿舍/食堂/快递快捷入口

## Phase 7 — 管理员地图编辑后台

- [ ] JWT / BCrypt 管理员认证
- [ ] 地图编辑器和 Geometry 校验
- [ ] POI / Building / Entrance / Path CRUD
- [ ] 未保存提示、撤销、删除确认
- [ ] 纠错审核和 Operation Log

## Phase 8 — AI Campus Map

- [ ] DeepSeek 适配器和环境变量密钥
- [ ] 结构化意图与实体解析
- [ ] SEARCH_POI / ROUTE / NEARBY / NEW_STUDENT
- [ ] session/IP/分钟级限流
- [ ] AI 不可用时降级
