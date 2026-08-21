import type { LayerSpecification } from 'maplibre-gl'

export const roadLayers: LayerSpecification[] = [
  {
    id: 'road-main-casing',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'ROAD_MAIN'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': '#c8c5bb', 'line-width': ['interpolate', ['linear'], ['zoom'], 14, 6, 19, 16] },
  },
  {
    id: 'road-main',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'ROAD_MAIN'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': '#fffdfa', 'line-width': ['interpolate', ['linear'], ['zoom'], 14, 4, 19, 12] },
  },
  {
    id: 'road-pedestrian',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'ROAD_PEDESTRIAN'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': '#ded4c2',
      'line-width': ['interpolate', ['linear'], ['zoom'], 14, 2, 19, 6],
      'line-dasharray': [1.5, 1.2],
    },
  },
]
