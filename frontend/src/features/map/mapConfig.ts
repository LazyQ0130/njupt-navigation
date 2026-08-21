import { setWorkerUrl, type MapOptions, type StyleSpecification } from 'maplibre-gl'
import mapLibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import type { CampusSummary } from '@/api/map'
import { MAP_PALETTE } from './mapPalette'
import type { CampusViewport } from './campusViewport'

export const CAMPUS_SOURCE_ID = 'campus-features'
export const USER_LOCATION_SOURCE_ID = 'user-location'
export const BUILDING_EXTRUSION_LAYER_ID = 'building-extrusion'

// MapLibre 6 resolves its worker next to import.meta.url. Vite bundles the main
// module under /assets, so the implicit sibling URL does not exist unless the
// worker is imported as an explicit bundled asset. `?worker&url` is important:
// plain `?url` copies only the entry module and drops its shared dependency.
export const MAPLIBRE_WORKER_URL = mapLibreWorkerUrl
setWorkerUrl(MAPLIBRE_WORKER_URL)

export const CAMPUS_ATTRIBUTION =
  '演示地图（非真实校园数据） · MapLibre'

export const MAP_STYLE: StyleSpecification = {
  version: 8,
  name: 'NJUPT light campus canvas',
  glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
  sources: {},
  layers: [
    {
      id: 'canvas-background',
      type: 'background',
      paint: {
        'background-color': MAP_PALETTE.background,
      },
    },
  ],
}

export function createMapOptions(
  container: HTMLElement,
  campus: CampusSummary,
  viewport?: CampusViewport,
): MapOptions {
  return {
    container,
    style: MAP_STYLE,
    center: viewport?.center ?? [campus.camera.longitude, campus.camera.latitude],
    zoom: campus.camera.zoom,
    pitch: campus.camera.pitch,
    bearing: campus.camera.bearing,
    minZoom: 14,
    maxZoom: 20,
    maxBounds: viewport?.bounds ?? [
      [campus.bounds.west, campus.bounds.south],
      [campus.bounds.east, campus.bounds.north],
    ],
    attributionControl: false,
    localIdeographFontFamily: 'Noto Sans CJK SC, Microsoft YaHei, sans-serif',
    cooperativeGestures: false,
  }
}
