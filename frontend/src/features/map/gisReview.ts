import type { FeatureCollection, Geometry } from 'geojson'

export const GIS_REVIEW_LAYER_KEYS = [
  'topology-gaps',
  'road-building-intersections',
  'unverified-buildings',
  'unverified-pois',
  'candidate-entrances',
] as const

export type GisReviewLayerKey = (typeof GIS_REVIEW_LAYER_KEYS)[number]
export type GisReviewCollections = Record<GisReviewLayerKey, FeatureCollection<Geometry>>

export function isGisReviewModeEnabled(
  search: string,
  buildAllowsReview = import.meta.env.DEV || import.meta.env.VITE_GIS_REVIEW_MODE === 'true',
): boolean {
  return buildAllowsReview && new URLSearchParams(search).get('debug') === 'gisp1'
}

export function activeReviewLayerKeys(reviewMode: boolean): GisReviewLayerKey[] {
  return reviewMode ? [...GIS_REVIEW_LAYER_KEYS] : []
}
