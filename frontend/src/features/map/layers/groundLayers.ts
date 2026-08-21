import type { LayerSpecification } from 'maplibre-gl'
import { MAP_PALETTE } from '../mapPalette'

export const groundLayers: LayerSpecification[] = [
  {
    id: 'campus-boundary-fill',
    type: 'fill',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'CAMPUS_BOUNDARY'],
    paint: { 'fill-color': MAP_PALETTE.campus, 'fill-opacity': 0.96 },
  },
  {
    id: 'ground-surfaces',
    type: 'fill',
    source: 'campus-features',
    filter: ['in', ['get', 'featureType'], ['literal', ['GREEN', 'WATER', 'SPORT', 'PLAZA']]],
    paint: {
      'fill-color': [
        'match',
        ['get', 'featureType'],
        'GREEN', MAP_PALETTE.green,
        'WATER', MAP_PALETTE.water,
        'SPORT', MAP_PALETTE.sport,
        'PLAZA', MAP_PALETTE.plaza,
        MAP_PALETTE.campus,
      ],
      'fill-opacity': 0.88,
      'fill-outline-color': 'rgba(82, 101, 117, 0.16)',
    },
  },
  {
    id: 'campus-boundary-line',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'CAMPUS_BOUNDARY'],
    paint: { 'line-color': MAP_PALETTE.boundary, 'line-width': 1.25, 'line-opacity': 0.58 },
  },
]
