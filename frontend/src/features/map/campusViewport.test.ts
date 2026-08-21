import { describe, expect, it } from 'vitest'
import type { CampusSummary } from '@/api/map'
import type { NormalizedFeatureCollection } from './types'
import { campusFitPadding, deriveCampusViewport } from './campusViewport'

const campus: CampusSummary = {
  id: 'campus-1',
  code: 'NJUPT_XIANLIN',
  name: '南京邮电大学仙林校区',
  camera: { longitude: 118.914, latitude: 32.104, zoom: 15.2, pitch: 52, bearing: -18 },
  bounds: { west: 118.9079, south: 32.0999, east: 118.9151, north: 32.106 },
  data: { buildings: 87, pois: 38, mapFeatures: 375 },
  layers: { buildings: true, ground: true, roads: true, pois: true },
}

describe('campus viewport', () => {
  it('derives bounds and center from the real Xianlin campus boundary', () => {
    const data = boundaryData([
      [118.9190578, 32.1064881],
      [118.9309571, 32.1064881],
      [118.9309571, 32.1241969],
      [118.9190578, 32.1241969],
      [118.9190578, 32.1064881],
    ])

    const viewport = deriveCampusViewport(data, campus)

    expect(viewport.derivedFromBoundary).toBe(true)
    expect(viewport.bounds).toEqual([
      [118.9190578, 32.1064881],
      [118.9309571, 32.1241969],
    ])
    expect(viewport.center[0]).toBeGreaterThan(viewport.bounds[0][0])
    expect(viewport.center[0]).toBeLessThan(viewport.bounds[1][0])
    expect(viewport.center[1]).toBeGreaterThan(viewport.bounds[0][1])
    expect(viewport.center[1]).toBeLessThan(viewport.bounds[1][1])
  })

  it('falls back to the saved campus camera and bounds without a valid boundary', () => {
    const viewport = deriveCampusViewport({ type: 'FeatureCollection', features: [] }, campus)

    expect(viewport.derivedFromBoundary).toBe(false)
    expect(viewport.center).toEqual([118.914, 32.104])
    expect(viewport.bounds).toEqual([[118.9079, 32.0999], [118.9151, 32.106]])
  })

  it('keeps useful fit padding on mobile and desktop', () => {
    expect(campusFitPadding(390)).toEqual({ top: 80, right: 28, bottom: 112, left: 28 })
    expect(campusFitPadding(1440)).toEqual({ top: 96, right: 96, bottom: 112, left: 96 })
  })
})

function boundaryData(ring: [number, number][]): NormalizedFeatureCollection {
  return {
    type: 'FeatureCollection',
    features: [{
      type: 'Feature',
      geometry: { type: 'Polygon', coordinates: [ring] },
      properties: {
        id: 'osm-way-89910254',
        featureType: 'CAMPUS_BOUNDARY',
        name: '南京邮电大学仙林校区',
      },
    }],
  }
}
