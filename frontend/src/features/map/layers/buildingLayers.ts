import type { ExpressionSpecification, LayerSpecification } from 'maplibre-gl'
import { BUILDING_EXTRUSION_LAYER_ID } from '../mapConfig'
import { MAP_PALETTE } from '../mapPalette'

const buildingColor: ExpressionSpecification = [
  'match',
  ['get', 'category'],
  ['LIBRARY', 'TEACHING'],
  MAP_PALETTE.buildingLibrary,
  ['DINING', 'SERVICE'],
  MAP_PALETTE.buildingService,
  MAP_PALETTE.building,
]

export const buildingLayers: LayerSpecification[] = [
  {
    id: 'building-footprint',
    type: 'fill',
    source: 'campus-features',
    filter: ['==', ['get', 'featureType'], 'BUILDING'],
    paint: { 'fill-color': MAP_PALETTE.buildingOutline, 'fill-opacity': 0.16 },
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
        MAP_PALETTE.selected,
        buildingColor,
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
    paint: { 'line-color': MAP_PALETTE.buildingOutline, 'line-width': 0.8, 'line-opacity': 0.64 },
  },
  {
    id: 'building-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 15,
    filter: ['all',
      ['==', ['get', 'featureType'], 'BUILDING'],
      ['!=', ['get', 'category'], 'DORMITORY'],
      ['==', ['coalesce', ['get', 'labelVisible'], true], true],
    ],
    layout: {
      'text-field': ['coalesce', ['get', 'displayName'], ['get', 'name']],
      'text-size': ['interpolate', ['linear'], ['zoom'], 15, 10, 17, 11.5, 19, 13.5],
      'text-font': ['Noto Sans Regular'],
      'text-max-width': 7.5,
      'text-allow-overlap': false,
      'text-ignore-placement': false,
      'symbol-sort-key': ['-', 100, ['coalesce', ['to-number', ['get', 'priority']], 0]],
    },
    paint: {
      'text-color': MAP_PALETTE.label,
      'text-halo-color': MAP_PALETTE.labelHalo,
      'text-halo-width': 1.35,
    },
  },
  {
    id: 'dormitory-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 17,
    filter: ['all',
      ['==', ['get', 'featureType'], 'BUILDING'],
      ['==', ['get', 'category'], 'DORMITORY'],
      ['==', ['coalesce', ['get', 'labelVisible'], true], true],
    ],
    layout: {
      'text-field': ['coalesce', ['get', 'displayName'], ['get', 'name']],
      'text-size': ['interpolate', ['linear'], ['zoom'], 17, 10, 19, 12],
      'text-font': ['Noto Sans Regular'],
      'text-max-width': 5,
      'text-allow-overlap': false,
      'text-ignore-placement': false,
      'symbol-sort-key': 80,
    },
    paint: {
      'text-color': MAP_PALETTE.label,
      'text-halo-color': MAP_PALETTE.labelHalo,
      'text-halo-width': 1.35,
    },
  },
]
