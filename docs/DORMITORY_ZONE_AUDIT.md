# Dormitory Zone Audit

The zone-to-number mapping is transcribed from the official NJUPT Xianlin campus map and matched
to the existing OSM-numbered dormitory polygons. `SOURCE_VERIFIED` means source-backed; it does not
mean manual or field verification.

No zone polygon is generated. Every zone geometry is a `Point` with
`geometryRole = LABEL_ONLY`; it is not valid for navigation or boundary decisions.

| Zone | Confirmed Building Anchors | Candidate Buildings | Source | Verification Status | Label Point Method |
| --- | --- | --- | --- | --- | --- |
| 梅苑 | 1号, 2号, 3号, 4号, 5号, 6号 | 1号, 2号, 3号, 4号, 5号, 6号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 6 building representative points |
| 兰苑 | 7号, 8号, 9号, 10号, 11号, 12号 | 7号, 8号, 9号, 10号, 11号, 12号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 6 building representative points |
| 竹苑 | 13号, 14号, 15号 | 13号, 14号, 15号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 3 building representative points |
| 菊苑 | 16号, 17号, 18号, 19号, 20号, 21号 | 16号, 17号, 18号, 19号, 20号, 21号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 6 building representative points |
| 桃苑 | 22号, 23号, 24号, 25号, 26号, 27号 | 22号, 23号, 24号, 25号, 26号, 27号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 6 building representative points |
| 李苑 | 28号, 29号, 30号, 31号, 32号, 33号 | 28号, 29号, 30号, 31号, 32号, 33号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 6 building representative points |
| 柳苑 | 34号, 35号, 36号, 37号, 38号, 39号 | 34号, 35号, 36号, 37号, 38号, 39号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 6 building representative points |
| 桂苑 | 40号, 41号, 42号, 43号, 44号, 45号 | 40号, 41号, 42号, 43号, 44号, 45号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 6 building representative points |
| 南荷 | 46号, 47号 | 46号, 47号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 2 building representative points |
| 北荷 | 48号, 49号 | 48号, 49号 | [NJUPT official campus map](https://www.njupt.edu.cn/_upload/article/images/eb/1f/e323ae9b457181e6874b1fc47842/d70d14a3-62d5-450d-9ec4-ae0ca836dc8c.jpg) + OSM polygons | SOURCE_VERIFIED | Arithmetic mean of 2 building representative points |

## Minimum manual confirmation checklist

Confirm only the two edge-number anchors below for each source-mapped zone, plus 青教公寓. This
covers the range boundaries without asking for a building-by-building review.

- 梅苑: 1号楼 / 6号楼
- 兰苑: 7号楼 / 12号楼
- 竹苑: 13号楼 / 15号楼
- 菊苑: 16号楼 / 21号楼
- 桃苑: 22号楼 / 27号楼
- 李苑: 28号楼 / 33号楼
- 柳苑: 34号楼 / 39号楼
- 桂苑: 40号楼 / 45号楼
- 南荷: 46号楼 / 47号楼
- 北荷: 48号楼 / 49号楼
- 青教公寓: confirm that it remains independent and is not assigned to a numbered dormitory zone

## Label-point limitations

The arithmetic mean is deterministic and derived only from representative points inside the source
building polygons. It is a cartographic anchor. It is not an inferred polygon, campus address, route
destination, or authoritative zone center.
