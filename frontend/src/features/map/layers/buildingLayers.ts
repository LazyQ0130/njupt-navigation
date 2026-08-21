import type { LayerSpecification } from 'maplibre-gl'
import { BUILDING_EXTRUSION_LAYER_ID } from '../mapConfig'

export const buildingLayers: LayerSpecification[] = [
  {
    id: 'building-footprint',
    type: 'fill',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'BUILDING'],
    paint: { 'fill-color': '#6c7e8e', 'fill-opacity': 0.26 },
  },
  {
    id: BUILDING_EXTRUSION_LAYER_ID,
    type: 'fill-extrusion',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'BUILDING'],
    paint: {
      'fill-extrusion-base': ['coalesce', ['to-number', ['get', 'minHeight']], 0],
      'fill-extrusion-height': ['coalesce', ['to-number', ['get', 'height']], 10],
      'fill-extrusion-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false],
        '#f59e0b',
        ['coalesce', ['get', 'color'], '#8fa7bf'],
      ],
      'fill-extrusion-opacity': 0.93,
      'fill-extrusion-vertical-gradient': true,
    },
  },
  {
    id: 'building-outline',
    type: 'line',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'BUILDING'],
    paint: { 'line-color': '#526576', 'line-width': 1.1, 'line-opacity': 0.7 },
  },
  {
    id: 'building-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 15.2,
    filter: ['==', ['get', 'featureType'], 'BUILDING'],
    layout: {
      'text-field': ['get', 'name'],
      'text-size': ['interpolate', ['linear'], ['zoom'], 15, 10, 18, 13],
      'text-font': ['Noto Sans Regular'],
      'text-max-width': 8,
      'text-allow-overlap': false,
      'text-ignore-placement': false,
      'symbol-sort-key': ['coalesce', ['to-number', ['get', 'priority']], 0],
    },
    paint: {
      'text-color': '#203248',
      'text-halo-color': 'rgba(255,255,255,0.92)',
      'text-halo-width': 1.5,
    },
  },
]
