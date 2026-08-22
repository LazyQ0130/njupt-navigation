import { describe, expect, it } from 'vitest'
import { buildingLayers } from './buildingLayers'

describe('building label hierarchy', () => {
  it('fades building numbers in from zoom 16.5 to 17', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'dormitory-building-labels')

    expect(layer?.type).toBe('symbol')
    expect(layer?.minzoom).toBe(16.5)
    expect(JSON.stringify(layer?.filter)).toContain('DORMITORY')
    expect(JSON.stringify(layer?.layout)).toContain('displayName')
    expect(JSON.stringify(layer?.layout)).toContain('false')
    expect(JSON.stringify(layer?.paint)).toContain('["zoom"],16.5,0,17,1')
  })

  it('shows label-only dormitory zones at medium zoom and fades them by 17.3', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'dormitory-zone-labels')
    const serialized = JSON.stringify(layer)

    expect(layer?.minzoom).toBe(15.5)
    expect(layer?.maxzoom).toBe(17.3)
    expect(serialized).toContain('DORMITORY_ZONE')
    expect(serialized).toContain('LABEL_ONLY')
    expect(serialized).toContain('["zoom"],15.5,0,15.7,1,16.8,1,17.3,0')
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
