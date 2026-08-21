import type { LayerSpecification } from 'maplibre-gl'
import { buildingLayers } from './buildingLayers'
import { groundLayers } from './groundLayers'
import { poiLayers } from './poiLayers'
import { roadLayers } from './roadLayers'

export const campusLayers: LayerSpecification[] = [
  ...groundLayers,
  ...roadLayers,
  ...buildingLayers,
  ...poiLayers,
]

export const campusVisualLayers = campusLayers.filter((layer) => layer.type !== 'symbol')
export const campusLabelLayers = campusLayers.filter((layer) => layer.type === 'symbol')
