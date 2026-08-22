import { describe, expect, it } from 'vitest'
import { poiLayers } from './poiLayers'

describe('POI label hierarchy', () => {
  it('defers commercial and duplicate building POIs until high zoom', () => {
    const layer = poiLayers.find((candidate) => candidate.id === 'poi-labels')
    const serialized = JSON.stringify(layer)

    expect(layer?.minzoom).toBe(17.4)
    expect(serialized).toContain('buildingId')
    expect(serialized).toContain('TEACHING')
    expect(serialized).toContain('DINING')
    expect(serialized).toContain('symbol-sort-key')
  })
})
