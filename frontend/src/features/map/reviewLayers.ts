import { type ExpressionSpecification, type Map, type MapLayerMouseEvent } from 'maplibre-gl'
import type { GisReviewCollections, GisReviewLayerKey } from './gisReview'
import type { ReviewLayerGroup, SelectedReview } from './types'

const severityColor: ExpressionSpecification = [
  'match',
  ['get', 'severity'],
  'P0',
  '#ef4444',
  'P1',
  '#f97316',
  '#facc15',
]

const sourceId = (key: GisReviewLayerKey) => `gis-review-${key}`

export const reviewLayerIds: Record<ReviewLayerGroup, string[]> = {
  buildings: ['building-footprint', 'building-extrusion', 'building-outline', 'building-labels'],
  roads: ['road-main-casing', 'road-main', 'road-pedestrian'],
  pois: ['poi-dots', 'poi-labels'],
  endpoints: ['review-topology-gaps'],
  intersections: ['review-road-building-intersections'],
  candidates: ['review-candidate-entrances'],
  verification: ['review-unverified-buildings', 'review-unverified-pois'],
}

export function addGisReviewLayers(
  map: Map,
  data: GisReviewCollections,
  onSelect?: (review: SelectedReview) => void,
): void {
  Object.entries(data).forEach(([key, collection]) => {
    map.addSource(sourceId(key as GisReviewLayerKey), { type: 'geojson', data: collection })
  })
  map.addLayer({
    id: 'review-unverified-buildings',
    type: 'line',
    source: sourceId('unverified-buildings'),
    paint: { 'line-color': severityColor, 'line-width': 2.5, 'line-opacity': 0.9 },
  })
  map.addLayer({
    id: 'review-unverified-pois',
    type: 'circle',
    source: sourceId('unverified-pois'),
    paint: { 'circle-color': severityColor, 'circle-radius': 6, 'circle-stroke-color': '#111827', 'circle-stroke-width': 1 },
  })
  map.addLayer({
    id: 'review-topology-gaps',
    type: 'circle',
    source: sourceId('topology-gaps'),
    paint: { 'circle-color': severityColor, 'circle-radius': 5, 'circle-stroke-color': '#111827', 'circle-stroke-width': 1.5 },
  })
  map.addLayer({
    id: 'review-road-building-intersections',
    type: 'line',
    source: sourceId('road-building-intersections'),
    paint: { 'line-color': severityColor, 'line-width': 5, 'line-opacity': 0.95 },
  })
  map.addLayer({
    id: 'review-candidate-entrances',
    type: 'circle',
    source: sourceId('candidate-entrances'),
    paint: { 'circle-color': severityColor, 'circle-radius': 7, 'circle-stroke-color': '#ffffff', 'circle-stroke-width': 2 },
  })

  if (!onSelect) return
  Object.values(reviewLayerIds).flat().filter((id) => id.startsWith('review-')).forEach((layerId) => {
    map.on('click', layerId, (event: MapLayerMouseEvent) => {
      const feature = event.features?.[0]
      if (!feature) return
      const properties = feature.properties ?? {}
      onSelect({
        id: String(properties.reviewId ?? feature.id ?? ''),
        name: String(properties.name ?? ''),
        source: String(properties.sourceObjectId ?? properties.dataSource ?? ''),
        verification: String(properties.currentVerificationStatus ?? properties.verificationStatus ?? ''),
        warning: String(properties.reason ?? ''),
        severity: String(properties.severity ?? ''),
      })
    })
  })
}

export function setReviewLayerVisibility(map: Map, group: ReviewLayerGroup, visible: boolean): void {
  reviewLayerIds[group].forEach((layerId) => {
    if (map.getLayer(layerId)) map.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none')
  })
}
