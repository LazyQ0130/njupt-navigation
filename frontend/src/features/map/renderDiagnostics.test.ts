import { describe, expect, it } from 'vitest'
import type { NormalizedFeatureCollection } from './types'
import { summarizeFeatureTypes } from './renderDiagnostics'

describe('campus render diagnostics', () => {
  it('reports every normalized campus feature type without silently dropping data', () => {
    const data = {
      type: 'FeatureCollection',
      features: [
        pointFeature('BUILDING'),
        pointFeature('BUILDING'),
        pointFeature('ROAD_MAIN'),
        pointFeature('GREEN'),
      ],
    } as NormalizedFeatureCollection

    expect(summarizeFeatureTypes(data)).toEqual({ BUILDING: 2, ROAD_MAIN: 1, GREEN: 1 })
  })
})

function pointFeature(featureType: 'BUILDING' | 'ROAD_MAIN' | 'GREEN') {
  return {
    type: 'Feature' as const,
    geometry: { type: 'Point' as const, coordinates: [118.92, 32.11] },
    properties: { id: featureType, featureType, name: featureType, priority: 0 },
  }
}
