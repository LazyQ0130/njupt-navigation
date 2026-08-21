import { describe, expect, it } from 'vitest'
import type { CampusFeatureCollection } from '@/api/map'
import { normalizeMapData } from './mapDataMapper'

describe('normalizeMapData', () => {
  it('keeps stable ids and applies safe building style fallbacks', () => {
    const input = {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        id: 'building-1',
        properties: {
          id: 'building-1', featureType: 'BUILDING', name: '测试楼',
          height: -2, minHeight: 4, color: 'invalid',
        },
        geometry: {
          type: 'Polygon',
          coordinates: [[[118.91, 32.10], [118.92, 32.10], [118.91, 32.10]]],
        },
      }],
    } as CampusFeatureCollection

    const result = normalizeMapData(input)

    expect(result.features[0]?.id).toBe('building-1')
    expect(result.features[0]?.properties.height).toBe(4)
    expect(result.features[0]?.properties.color).toBe('#8fa7bf')
  })

  it('drops unsupported future feature types without breaking the map', () => {
    const input = {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature', id: 'future-1',
        properties: { id: 'future-1', featureType: 'ROUTE', name: '未来路线' },
        geometry: { type: 'Point', coordinates: [118.91, 32.1] },
      }],
    } as CampusFeatureCollection

    expect(normalizeMapData(input).features).toHaveLength(0)
  })
})
