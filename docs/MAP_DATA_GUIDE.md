# 南邮仙林校区地图数据采集与导入说明

## 数据优先级

1. 可合法使用的 OpenStreetMap 数据作为初始轮廓；
2. 学校公开材料仅作人工核对参考，并登记来源/许可；
3. 实地 GPS、照片和步行核验补齐入口、小路和通行属性；
4. 管理后台持续维护施工、封路、改名等变化。

不得抓取或分发商业地图瓦片，也不得未经授权批量复制其受版权保护的数据。

## 每批数据必须记录

- 来源 URL/文件和许可
- 获取/采集日期
- 原始坐标系
- 采集人和核验人
- 预计精度
- 转换或简化步骤
- 已知缺陷

## 坐标规范

数据库统一使用 WGS84 / EPSG:4326。GeoJSON 坐标顺序必须是 `[longitude, latitude]`。仙林校区合理范围应接近南京；导入器会做基本经纬度及 Geometry 合法性检查，但不能替代人工叠图核验。

若来源是 GCJ-02 或 BD-09，必须在独立转换流程中转为 WGS84，并把算法、版本和误差记录在批次元数据中，禁止静默混用。

## Phase 0 GeoJSON 约定

根对象是 `FeatureCollection`。每个 Feature 使用 `properties.featureType` 标识：

### Building

```json
{
  "type": "Feature",
  "properties": {
    "featureType": "BUILDING",
    "campusCode": "NJUPT_XIANLIN",
    "externalId": "survey-building-001",
    "name": "示例教学楼",
    "aliases": ["示例楼"],
    "category": "TEACHING",
    "height": 18,
    "minHeight": 0,
    "color": "#D7E3F4",
    "enabled": true
  },
  "geometry": { "type": "Polygon", "coordinates": [] }
}
```

### POI

```json
{
  "type": "Feature",
  "properties": {
    "featureType": "POI",
    "campusCode": "NJUPT_XIANLIN",
    "externalId": "survey-poi-001",
    "name": "示例地点",
    "aliases": ["示例"],
    "keywords": ["服务"],
    "category": "SERVICE",
    "enabled": true
  },
  "geometry": { "type": "Point", "coordinates": [118.9, 32.1] }
}
```

`externalId` 在同一数据类型内唯一，使重复导入可以更新而不是产生副本。

## 导入前检查

- 确认坐标系和经纬度顺序；
- Polygon 闭合且无自交，Point 落在校园合理范围；
- 名称、分类、campusCode、externalId 存在；
- 建筑高度为非负数且 `minHeight <= height`；
- 抽样叠加到已知控制点，确认无整体偏移；
- 不把建筑中心当作入口；入口将在后续独立采集。

## Phase 1 前需要人工提供/核验

- 校园边界和主校门位置；
- 所有主要建筑 Polygon、正式名称、别名、用途和大致高度；
- 建筑主要入口 Point 与步行/骑行/无障碍属性；
- 校内道路、人行小路及禁行/夜间通行状态；
- 草坪、水体、运动场区域；
- 数据来源与授权情况；
- 现场照片或标注，用于校验建筑颜色和相对高度。

