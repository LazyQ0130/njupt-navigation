import { describe, expect, it } from 'vitest'
import { buildingLayers } from './buildingLayers'
import { campusLabelLayers } from '.'

const DEFAULT_CAMPUS_OVERVIEW_ZOOM = 15.2

describe('building label hierarchy', () => {
  it('fades building numbers in from zoom 16.5 to 17', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'dormitory-building-labels')

    expect(layer?.type).toBe('symbol')
    expect(layer?.minzoom).toBe(16.5)
    expect(JSON.stringify(layer?.filter)).toContain('DORMITORY')
    expect(JSON.stringify(layer?.layout)).toContain('displayName')
    expect(JSON.stringify(layer?.layout)).toContain('false')
    expect(JSON.stringify(layer?.paint)).toContain('["zoom"],16.5,0,17,1')
    expect(layer?.minzoom).toBeGreaterThan(DEFAULT_CAMPUS_OVERVIEW_ZOOM)
  })

  it('shows label-only dormitory zones at the default campus overview zoom', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'dormitory-zone-labels')
    const serialized = JSON.stringify(layer)

    expect(layer?.minzoom).toBe(14.8)
    expect(layer?.maxzoom).toBe(17.2)
    expect(layer?.minzoom).toBeLessThan(DEFAULT_CAMPUS_OVERVIEW_ZOOM)
    expect(layer?.maxzoom).toBeGreaterThan(DEFAULT_CAMPUS_OVERVIEW_ZOOM)
    expect(serialized).toContain('DORMITORY_ZONE')
    expect(serialized).toContain('LABEL_ONLY')
    expect(serialized).toContain('["zoom"],14.8,0,15,1,16.5,1,17.2,0')
    expect(interpolateZoomOpacity(layer, DEFAULT_CAMPUS_OVERVIEW_ZOOM)).toBeGreaterThan(0)
  })

  it('adds symbol layers from lowest to highest MapLibre collision priority', () => {
    expect(campusLabelLayers.map((layer) => layer.id)).toEqual([
      'poi-labels',
      'building-labels',
      'dormitory-building-labels',
      'dormitory-zone-labels',
      'core-campus-labels',
    ])
  })

  it('gives teaching buildings and other core landmarks their own highest-priority layer', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'core-campus-labels')
    const serialized = JSON.stringify(layer)

    expect(layer?.minzoom).toBe(14.5)
    for (const name of ['教1', '教2', '教3', '教4', '教5', '圆楼']) {
      expect(serialized).toContain(name)
    }
    expect(serialized).toContain('symbol-sort-key')
    expect(serialized).toContain(':0')
    expect(serialized).toContain('text-variable-anchor')
  })

  it('uses displayName fallback and labelVisible suppression for normal labels', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'building-labels')
    const serialized = JSON.stringify(layer)

    expect(serialized).toContain('displayName')
    expect(serialized).toContain('labelVisible')
    expect(serialized).toContain('DORMITORY')
    expect(serialized).toContain('教1')
  })
})

function interpolateZoomOpacity(layer: (typeof buildingLayers)[number] | undefined, zoom: number) {
  if (!layer || layer.type !== 'symbol') return 0
  const opacity = layer.paint?.['text-opacity']
  if (!Array.isArray(opacity) || opacity[0] !== 'interpolate') return 1
  const stops = opacity.slice(3) as number[]
  for (let index = 0; index < stops.length - 2; index += 2) {
    const lowerZoom = stops[index]
    const lowerOpacity = stops[index + 1]
    const upperZoom = stops[index + 2]
    const upperOpacity = stops[index + 3]
    if (zoom <= upperZoom) {
      const progress = (zoom - lowerZoom) / (upperZoom - lowerZoom)
      return lowerOpacity + progress * (upperOpacity - lowerOpacity)
    }
  }
  return stops.at(-1) ?? 0
}
