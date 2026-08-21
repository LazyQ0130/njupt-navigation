import type { Feature, Geometry } from 'geojson'
import type { CampusFeatureCollection, CampusFeatureProperties } from '@/api/map'
import {
  SUPPORTED_FEATURE_TYPES,
  type NormalizedFeatureCollection,
  type SupportedFeatureType,
} from './types'

const DEFAULT_BUILDING_COLOR = '#8fa7bf'
const DEFAULT_FEATURE_NAME = '未命名要素'

export function normalizeMapData(input: CampusFeatureCollection): NormalizedFeatureCollection {
  if (input.type !== 'FeatureCollection' || !Array.isArray(input.features)) {
    throw new Error('地图数据不是有效的 GeoJSON FeatureCollection')
  }

  const features = input.features.flatMap((feature, index) => {
    const normalized = normalizeFeature(feature, index)
    return normalized ? [normalized] : []
  })

  return { type: 'FeatureCollection', features }
}

function normalizeFeature(
  feature: Feature<Geometry, CampusFeatureProperties>,
  index: number,
): Feature<Geometry, CampusFeatureProperties> | null {
  if (!feature.geometry || !feature.properties) {
    return null
  }

  const featureType = String(feature.properties.featureType ?? '').toUpperCase()
  if (!isSupportedFeatureType(featureType)) {
    return null
  }

  const stableId = String(feature.id ?? feature.properties.id ?? `map-feature-${index}`)
  const properties: CampusFeatureProperties = {
    ...feature.properties,
    id: stableId,
    featureType,
    name: String(feature.properties.name || DEFAULT_FEATURE_NAME),
    priority: numberOr(feature.properties.priority, 0),
  }

  if (featureType === 'BUILDING') {
    const minHeight = Math.max(0, numberOr(properties.minHeight, 0))
    properties.minHeight = minHeight
    properties.height = Math.max(minHeight, numberOr(properties.height, 10))
    properties.color = validHexColor(properties.color) ? properties.color : DEFAULT_BUILDING_COLOR
  }

  return {
    type: 'Feature',
    id: stableId,
    geometry: feature.geometry,
    properties,
  }
}

function isSupportedFeatureType(value: string): value is SupportedFeatureType {
  return (SUPPORTED_FEATURE_TYPES as readonly string[]).includes(value)
}

function numberOr(value: unknown, fallback: number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function validHexColor(value: unknown): value is string {
  return typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value)
}
