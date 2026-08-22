import type { ExpressionSpecification, LayerSpecification } from 'maplibre-gl'
import { BUILDING_EXTRUSION_LAYER_ID } from '../mapConfig'
import { MAP_PALETTE } from '../mapPalette'

export const CORE_CAMPUS_LABELS = [
  '教1', '教2', '教3', '教4', '教5', '圆楼', '图书馆',
  '一食堂', '二食堂', '三食堂', '行政楼', '行政北楼', '行政南楼',
]

const displayNameExpression: ExpressionSpecification = [
  'coalesce', ['get', 'displayName'], ['get', 'name'],
]

const isCoreCampusLabel: ExpressionSpecification = [
  'in', displayNameExpression, ['literal', CORE_CAMPUS_LABELS],
]

const buildingColor: ExpressionSpecification = [
  'match',
  ['get', 'category'],
  ['LIBRARY', 'TEACHING'],
  MAP_PALETTE.buildingLibrary,
  ['DINING', 'SERVICE'],
  MAP_PALETTE.buildingService,
  MAP_PALETTE.building,
]

export const buildingVisualLayers: LayerSpecification[] = [
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
]

export const ordinaryBuildingLabelLayers: LayerSpecification[] = [
  {
    id: 'building-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 15,
    filter: ['all',
      ['==', ['get', 'featureType'], 'BUILDING'],
      ['!=', ['get', 'category'], 'DORMITORY'],
      ['!', isCoreCampusLabel],
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
]

export const dormitoryBuildingLabelLayers: LayerSpecification[] = [
  {
    id: 'dormitory-building-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 16.5,
    filter: ['all',
      ['==', ['get', 'featureType'], 'BUILDING'],
      ['==', ['get', 'category'], 'DORMITORY'],
      ['==', ['coalesce', ['get', 'labelVisible'], true], true],
    ],
    layout: {
      'text-field': ['coalesce', ['get', 'displayName'], ['get', 'name']],
      'text-size': ['interpolate', ['linear'], ['zoom'], 16.5, 9.5, 19, 12],
      'text-font': ['Noto Sans Regular'],
      'text-max-width': 5,
      'text-allow-overlap': false,
      'text-ignore-placement': false,
      'symbol-sort-key': 60,
    },
    paint: {
      'text-color': MAP_PALETTE.label,
      'text-halo-color': MAP_PALETTE.labelHalo,
      'text-halo-width': 1.35,
      'text-opacity': ['interpolate', ['linear'], ['zoom'], 16.5, 0, 17, 1],
    },
  },
]

export const dormitoryZoneLabelLayers: LayerSpecification[] = [
  {
    id: 'dormitory-zone-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 14.8,
    maxzoom: 17.2,
    filter: ['all',
      ['==', ['get', 'featureType'], 'DORMITORY_ZONE'],
      ['==', ['get', 'geometryRole'], 'LABEL_ONLY'],
      ['==', ['coalesce', ['get', 'labelVisible'], true], true],
    ],
    layout: {
      'text-field': displayNameExpression,
      'text-size': ['interpolate', ['linear'], ['zoom'], 14.8, 14, 16.5, 16],
      'text-font': ['Noto Sans Regular'],
      'text-letter-spacing': 0.08,
      'text-max-width': 5,
      'text-allow-overlap': false,
      'text-ignore-placement': false,
      'symbol-sort-key': 20,
    },
    paint: {
      'text-color': MAP_PALETTE.label,
      'text-halo-color': MAP_PALETTE.labelHalo,
      'text-halo-width': 1.7,
      'text-opacity': [
        'interpolate', ['linear'], ['zoom'],
        14.8, 0,
        15, 1,
        16.5, 1,
        17.2, 0,
      ],
    },
  },
]

export const coreCampusLabelLayers: LayerSpecification[] = [
  {
    id: 'core-campus-labels',
    type: 'symbol',
    source: 'campus-features',
    minzoom: 14.5,
    filter: ['all',
      ['==', ['get', 'featureType'], 'BUILDING'],
      ['==', ['coalesce', ['get', 'labelVisible'], true], true],
      isCoreCampusLabel,
    ],
    layout: {
      'text-field': displayNameExpression,
      'text-size': ['interpolate', ['linear'], ['zoom'], 14.5, 11, 17, 12.5, 19, 14],
      'text-font': ['Noto Sans Regular'],
      'text-max-width': 7,
      'text-allow-overlap': false,
      'text-ignore-placement': false,
      'text-variable-anchor': ['center', 'top', 'bottom', 'left', 'right'],
      'text-radial-offset': 0.15,
      'symbol-sort-key': 0,
    },
    paint: {
      'text-color': MAP_PALETTE.label,
      'text-halo-color': MAP_PALETTE.labelHalo,
      'text-halo-width': 1.6,
    },
  },
]

export const buildingLayers: LayerSpecification[] = [
  ...buildingVisualLayers,
  ...ordinaryBuildingLabelLayers,
  ...dormitoryBuildingLabelLayers,
  ...dormitoryZoneLabelLayers,
  ...coreCampusLabelLayers,
]
