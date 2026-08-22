import type { LayerSpecification } from 'maplibre-gl'
import {
  buildingVisualLayers,
  coreCampusLabelLayers,
  dormitoryBuildingLabelLayers,
  dormitoryZoneLabelLayers,
  ordinaryBuildingLabelLayers,
} from './buildingLayers'
import { groundLayers } from './groundLayers'
import { poiLabelLayers, poiVisualLayers } from './poiLayers'
import { roadLayers } from './roadLayers'

export const campusVisualLayers: LayerSpecification[] = [
  ...groundLayers,
  ...roadLayers,
  ...buildingVisualLayers,
  ...poiVisualLayers,
]

// MapLibre places symbol layers from the end of the style stack to the beginning.
// Keep this list explicitly ordered from lowest to highest collision priority.
export const campusLabelLayers: LayerSpecification[] = [
  ...poiLabelLayers,
  ...ordinaryBuildingLabelLayers,
  ...dormitoryBuildingLabelLayers,
  ...dormitoryZoneLabelLayers,
  ...coreCampusLabelLayers,
]

export const campusLayers: LayerSpecification[] = [
  ...campusVisualLayers,
  ...campusLabelLayers,
]
