import type { LayerSpecification } from 'maplibre-gl'
import { MAP_PALETTE } from '../mapPalette'

export const poiVisualLayers: LayerSpecification[] = [
  {
    id: 'poi-dots',
    type: 'circle',
    source: 'campus-features',
    minzoom: 16,
    filter: ['all', ['==', ['get', 'featureType'], 'POI'], ['==', ['coalesce', ['get', 'labelVisible'], true], true]],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 16, 3.5, 18, 5.5],
      'circle-color': MAP_PALETTE.poi,
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 2,
    },
  },
]

export const poiLabelLayers: LayerSpecification[] = [
  {
    id: 'poi-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 17.4,
    filter: ['all',
      ['==', ['get', 'featureType'], 'POI'],
      ['==', ['coalesce', ['get', 'labelVisible'], true], true],
      ['!', ['all',
        ['has', 'buildingId'],
        ['in', ['get', 'category'], ['literal', ['TEACHING', 'LIBRARY', 'DINING', 'ADMINISTRATION']]],
      ]],
    ],
    layout: {
      'text-field': ['coalesce', ['get', 'displayName'], ['get', 'name']],
      'text-font': ['Noto Sans Regular'],
      'text-size': ['interpolate', ['linear'], ['zoom'], 17.4, 10, 19, 11.5],
      'text-offset': [0, 1.15],
      'text-anchor': 'top',
      'text-allow-overlap': false,
      'symbol-sort-key': ['-', 140, ['coalesce', ['to-number', ['get', 'priority']], 0]],
    },
    paint: {
      'text-color': MAP_PALETTE.labelMuted,
      'text-halo-color': MAP_PALETTE.labelHalo,
      'text-halo-width': 1.4,
    },
  },
]

export const poiLayers: LayerSpecification[] = [
  ...poiVisualLayers,
  ...poiLabelLayers,
]
