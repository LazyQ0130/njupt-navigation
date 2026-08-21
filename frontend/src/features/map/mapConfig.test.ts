import { describe, expect, it } from 'vitest'
import type { CampusSummary } from '@/api/map'
import { getWorkerUrl } from 'maplibre-gl'
import { CAMPUS_ATTRIBUTION, MAP_STYLE, MAPLIBRE_WORKER_URL, createMapOptions } from './mapConfig'

const campus: CampusSummary = {
  id: 'campus-1',
  code: 'NJUPT_XIANLIN',
  name: '测试校区',
  camera: { longitude: 118.91, latitude: 32.1, zoom: 16, pitch: 52, bearing: -18 },
  bounds: { west: 118.90, south: 32.09, east: 118.92, north: 32.11 },
  data: { buildings: 1, pois: 1, mapFeatures: 1 },
  layers: { buildings: true, ground: true, roads: true, pois: true },
}

describe('map config', () => {
  it('uses the camera and bounds returned by bootstrap API', () => {
    const options = createMapOptions(document.createElement('div'), campus)

    expect(options.center).toEqual([118.91, 32.1])
    expect(options.pitch).toBe(52)
    expect(options.maxBounds).toEqual([[118.90, 32.09], [118.92, 32.11]])
  })

  it('uses a real-boundary viewport instead of stale bootstrap coordinates', () => {
    const options = createMapOptions(document.createElement('div'), campus, {
      bounds: [[118.919, 32.106], [118.931, 32.124]],
      center: [118.925, 32.115],
      derivedFromBoundary: true,
    })

    expect(options.center).toEqual([118.925, 32.115])
    expect(options.maxBounds).toEqual([[118.919, 32.106], [118.931, 32.124]])
  })

  it('uses a key-free canvas style with explicit attribution', () => {
    expect(MAP_STYLE.sources).toEqual({})
    expect(MAP_STYLE.layers[0]?.type).toBe('background')
    expect(CAMPUS_ATTRIBUTION).toContain('演示地图')
    expect(CAMPUS_ATTRIBUTION).toContain('非真实校园数据')
  })

  it('configures an explicit Vite asset URL for the MapLibre worker', () => {
    expect(MAPLIBRE_WORKER_URL).toContain('maplibre-gl-worker')
    expect(getWorkerUrl()).toBe(MAPLIBRE_WORKER_URL)
  })
})
