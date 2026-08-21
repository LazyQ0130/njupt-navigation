import type { LayerSpecification } from 'maplibre-gl'

export const poiLayers: LayerSpecification[] = [
  {
    id: 'poi-dots',
    type: 'circle',
    source: 'campus-features',
    minzoom: 15.5,
    filter: ['==', ['get', 'featureType'], 'POI'],
    paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 15, 3.5, 18, 6],
      'circle-color': '#e85d3f',
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 2,
    },
  },
  {
    id: 'poi-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 16.2,
    filter: ['==', ['get', 'featureType'], 'POI'],
    layout: {
      'text-field': ['get', 'name'],
      'text-font': ['Noto Sans Regular'],
      'text-size': 11,
      'text-offset': [0, 1.15],
      'text-anchor': 'top',
      'text-allow-overlap': false,
      'symbol-sort-key': ['coalesce', ['to-number', ['get', 'priority']], 0],
    },
    paint: {
      'text-color': '#344155',
      'text-halo-color': '#ffffff',
      'text-halo-width': 1.4,
    },
  },
]
