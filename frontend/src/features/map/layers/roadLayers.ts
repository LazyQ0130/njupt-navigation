import type { LayerSpecification } from 'maplibre-gl'
import { MAP_PALETTE } from '../mapPalette'

export const roadLayers: LayerSpecification[] = [
  {
    id: 'road-main-casing',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'ROAD_MAIN'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': MAP_PALETTE.roadCasing, 'line-width': ['interpolate', ['linear'], ['zoom'], 14, 5, 19, 15] },
  },
  {
    id: 'road-main',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'ROAD_MAIN'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: { 'line-color': MAP_PALETTE.road, 'line-width': ['interpolate', ['linear'], ['zoom'], 14, 3.2, 19, 11.5] },
  },
  {
    id: 'road-pedestrian',
    type: 'line',
    source: 'campus-features',
    minzoom: 15.6,
    filter: ['==', ['get', 'featureType'], 'ROAD_PEDESTRIAN'],
    layout: { 'line-cap': 'round', 'line-join': 'round' },
    paint: {
      'line-color': MAP_PALETTE.path,
      'line-width': ['interpolate', ['linear'], ['zoom'], 15.6, 1.5, 19, 5],
      'line-dasharray': [1.5, 1.2],
    },
  },
]
