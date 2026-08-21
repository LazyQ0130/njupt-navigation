import type { MapOptions, StyleSpecification } from 'maplibre-gl'
import type { CampusSummary } from '@/api/map'

export const CAMPUS_SOURCE_ID = 'campus-features'
export const USER_LOCATION_SOURCE_ID = 'user-location'
export const BUILDING_EXTRUSION_LAYER_ID = 'building-extrusion'

export const CAMPUS_ATTRIBUTION =
  'Phase 1 synthetic demo data · Map rendering by MapLibre'

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
        'background-color': '#edf1ea',
      },
    },
  ],
}

export function createMapOptions(container: HTMLElement, campus: CampusSummary): MapOptions {
  return {
    container,
    style: MAP_STYLE,
    center: [campus.camera.longitude, campus.camera.latitude],
    zoom: campus.camera.zoom,
    pitch: campus.camera.pitch,
    bearing: campus.camera.bearing,
    minZoom: 14,
    maxZoom: 20,
    maxBounds: [
      [campus.bounds.west, campus.bounds.south],
      [campus.bounds.east, campus.bounds.north],
    ],
    attributionControl: false,
    localIdeographFontFamily: 'Noto Sans CJK SC, Microsoft YaHei, sans-serif',
    cooperativeGestures: false,
  }
}
