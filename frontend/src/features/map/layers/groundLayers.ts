import type { LayerSpecification } from 'maplibre-gl'

export const groundLayers: LayerSpecification[] = [
  {
    id: 'campus-boundary-fill',
    type: 'fill',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'CAMPUS_BOUNDARY'],
    paint: { 'fill-color': '#e8ede4', 'fill-opacity': 0.88 },
  },
  {
    id: 'ground-surfaces',
    type: 'fill',
    source: 'campus-features',
    filter: ['in', ['get', 'featureType'], ['literal', ['GREEN', 'WATER', 'SPORT', 'PLAZA']]],
    paint: {
      'fill-color': [
        'coalesce',
        ['get', 'color'],
        ['match', ['get', 'featureType'], 'WATER', '#9ccbe0', 'SPORT', '#a8c9a8', '#bfd7b7'],
      ],
      'fill-opacity': 0.9,
      'fill-outline-color': 'rgba(71, 95, 75, 0.18)',
    },
  },
  {
    id: 'campus-boundary-line',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'CAMPUS_BOUNDARY'],
    paint: { 'line-color': '#365a4a', 'line-width': 2, 'line-opacity': 0.7 },
  },
]
