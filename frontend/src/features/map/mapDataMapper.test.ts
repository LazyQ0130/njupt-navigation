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

  it('preserves displayName and allows a safe fallback to name', () => {
    const input = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature', id: 'short', properties: {
            id: 'short', featureType: 'BUILDING', name: '教学2号楼', displayName: '教2',
          }, geometry: { type: 'Point', coordinates: [118.91, 32.1] },
        },
        {
          type: 'Feature', id: 'fallback', properties: {
            id: 'fallback', featureType: 'POI', name: '图书馆',
          }, geometry: { type: 'Point', coordinates: [118.92, 32.1] },
        },
      ],
    } as CampusFeatureCollection

    const result = normalizeMapData(input)

    expect(result.features[0]?.properties.displayName).toBe('教2')
    expect(result.features[1]?.properties.displayName ?? result.features[1]?.properties.name).toBe('图书馆')
  })

  it('normalizes dormitory zone label features without losing their semantic role', () => {
    const input = {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature', id: 'zone-liu', properties: {
          id: 'zone-liu', featureType: 'dormitory_zone', name: '柳苑',
          displayName: '柳苑', geometryRole: 'LABEL_ONLY',
        }, geometry: { type: 'Point', coordinates: [118.9291, 32.1203] },
      }],
    } as CampusFeatureCollection

    const [zone] = normalizeMapData(input).features

    expect(zone?.properties.featureType).toBe('DORMITORY_ZONE')
    expect(zone?.properties.displayName).toBe('柳苑')
    expect(zone?.properties.geometryRole).toBe('LABEL_ONLY')
  })
})
