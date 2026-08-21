import { describe, expect, it } from 'vitest'
import { buildingLayers } from './buildingLayers'

describe('building label hierarchy', () => {
  it('keeps dormitories in a separate zoom-17 label layer', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'dormitory-labels')

    expect(layer?.type).toBe('symbol')
    expect(layer?.minzoom).toBe(17)
    expect(JSON.stringify(layer?.filter)).toContain('DORMITORY')
    expect(JSON.stringify(layer?.layout)).toContain('displayName')
    expect(JSON.stringify(layer?.layout)).toContain('false')
  })

  it('uses displayName fallback and labelVisible suppression for normal labels', () => {
    const layer = buildingLayers.find((candidate) => candidate.id === 'building-labels')
    const serialized = JSON.stringify(layer)

    expect(serialized).toContain('displayName')
    expect(serialized).toContain('labelVisible')
    expect(serialized).toContain('DORMITORY')
  })
})
