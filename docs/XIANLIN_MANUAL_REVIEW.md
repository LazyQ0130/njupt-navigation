# 仙林校区人工审核清单

核验结果先填写 `data/real/xianlin/manual/field-review-template.csv`，再运行 `python scripts/gis/apply_field_review.py --input <field-review.csv> --reviewed-at <ISO-8601>`。肉眼对照公开资料使用 `MANUALLY_REVIEWED`，亲临现场确认使用 `FIELD_VERIFIED`；不要修改 raw OSM 或直接编辑 normalized GeoJSON。

## P0：校界与校门

- [ ] Campus Boundary（OSM way `89910254`）
  - [ ] Polygon 与当前围墙/校属区域整体一致
  - [ ] 南门、北门位置落在合理的校界段
  - [ ] 西南与东北边缘没有明显遗漏或多包区域
- [ ] 南门
  - [ ] 正式名称与别名
  - [ ] Point / 校界位置
  - [ ] 步行、骑行、车辆通行（未知保持 NULL）
  - [ ] 开放时间（不能确认则保持 NULL）
- [ ] 北门
  - [ ] 正式名称与别名
  - [ ] Point / 校界位置
  - [ ] 步行、骑行、车辆通行（未知保持 NULL）
  - [ ] 开放时间（不能确认则保持 NULL）

## P0：教学与公共建筑

对教1、教2、教3、教4、教5逐栋执行：

- [ ] 正式名称与当前 Polygon 对应
- [ ] 学生常用简称与别名（如教一/教学1号楼）
- [ ] 主要入口的大致位置
- [ ] 入口到附近步道是否连续且不穿墙
- [ ] 入口通行属性；未知值保持 NULL

对图书馆、圆楼、行政楼、大学生活动中心、青春剧场、新体育馆逐栋执行：

- [ ] 正式名称和当前用途
- [ ] Polygon 与实际建筑一致
- [ ] 主要入口和无障碍入口
- [ ] 附近道路连通与夜间限制
- [ ] 别名

特别检查：

- [ ] 教5 的两个工程候选入口是否为真实主要入口
- [ ] 行政楼办公楼候选入口是否属于正确 Polygon
- [ ] `osm:way:970894656` 穿教1是否为 covered/tunnel 通道
- [ ] `osm:way:224954286` 穿两个“连廊”是否为建筑下方/内部通道

## P0：路网与道路穿建筑

- [ ] `osm:way:223699479` 与 `osm:way:964850646` 相距 0.79m/1.56m 的端点是否应合并
- [ ] `osm:way:224941322` 穿“主席台”4.14m：道路偏移还是建筑 Polygon 过大
- [ ] 25 个 P1、70 个 P2 端点按 `review/topology-gaps.geojson` 抽查，不把正常 dead end 强行连接
- [ ] 鼎新大道、教学区主路、宿舍区道路的步行/骑行限制；无明确来源保持 UNKNOWN

## 宿舍与生活设施

对 1—49 号数字建筑按楼组核验，不要求本阶段逐入口完成：

- [ ] 编号与 Polygon 对应
- [ ] 是否确为宿舍
- [ ] `displayName` 与常用别名
- [ ] 一栋多编号或命名不清时标记 `AMBIGUOUS`，不强制一对一

对一、二、三、四食堂逐个核验：

- [ ] 正式名称和学生常用名
- [ ] Building / POI 对应关系
- [ ] 当前是否仍营业
- [ ] 主要入口和附近道路

对收发室、快递点、超市、商铺逐个核验：

- [ ] 位置和名称仍有效
- [ ] `freshnessStatus` 与 `lastVerifiedAt`
- [ ] 仅有 OSM 来源时保持 `SOURCE_VERIFIED`

## 入口记录要求

- [ ] 正式入口状态至少是 `MANUALLY_REVIEWED` 或 `FIELD_VERIFIED`
- [ ] 入口距离所属建筑边界不超过 3m；超过则记录 warning 并复查 buildingId
- [ ] 记录最近 Road / Footpath；超过 10m 标为 P0/P1
- [ ] walking/cycling/accessible/vehicleAccess 无证据时保持 NULL
- [ ] 不从 candidate 自动生成正式 Entrance，不在本阶段创建 Route Edge

## 完成定义

- [ ] 每条记录包含 `reviewedBy`、`reviewedAt` 和原因/备注
- [ ] `dataSource=OSM` 等来源血缘未被人工状态覆盖
- [ ] 重新 build 后 topology/validation report 与 manual 文件一致
- [ ] 现场路线 A/B/C 记录已汇总，P0 均已处理或给出明确解释
