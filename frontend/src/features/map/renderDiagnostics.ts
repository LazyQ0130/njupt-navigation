import type { Map } from 'maplibre-gl'
import type { NormalizedFeatureCollection } from './types'
import { CAMPUS_SOURCE_ID } from './mapConfig'
import { CORE_CAMPUS_LABELS } from './layers/buildingLayers'
import { campusLabelLayers, campusVisualLayers } from './layers'

export interface CampusRenderDiagnostics {
  apiFeatureCount: number
  apiFeatureTypes: Record<string, number>
  sourceExists: boolean
  sourceLoaded: boolean
  sourceFeatureCount: number
  renderedFeatureCount: number
  renderedFeatureTypes: Record<string, number>
  renderedLayers: Record<string, number>
  visualLayers: Record<string, boolean>
  labelLayers: Record<string, boolean>
  dormitoryZoneSourceFeatureCount: number
  renderedDormitoryZoneLabelCount: number
  renderedCoreCampusLabelNames: string[]
  center: { longitude: number; latitude: number }
  zoom: number
  canvas: { width: number; height: number }
}

declare global {
  interface Window {
    __NJUPT_CAMPUS_MAP__?: Map
    __NJUPT_MAP_DIAGNOSTICS__?: CampusRenderDiagnostics
  }
}

export function summarizeFeatureTypes(data: NormalizedFeatureCollection): Record<string, number> {
  return data.features.reduce<Record<string, number>>((summary, feature) => {
    const featureType = feature.properties.featureType
    summary[featureType] = (summary[featureType] ?? 0) + 1
    return summary
  }, {})
}

export function captureRenderDiagnostics(
  map: Map,
  data: NormalizedFeatureCollection,
): CampusRenderDiagnostics {
  const visualLayers = Object.fromEntries(
    campusVisualLayers.map((layer) => [layer.id, Boolean(map.getLayer(layer.id))]),
  )
  const activeLayerIds = Object.entries(visualLayers)
    .filter(([, exists]) => exists)
    .map(([id]) => id)
  const center = map.getCenter()
  const canvasBounds = map.getCanvas().getBoundingClientRect()
  const renderedFeatures = activeLayerIds.length > 0
    ? map.queryRenderedFeatures({ layers: activeLayerIds })
    : []
  const labelLayers = Object.fromEntries(
    campusLabelLayers.map((layer) => [layer.id, Boolean(map.getLayer(layer.id))]),
  )
  const renderedLabelFeatures = map.queryRenderedFeatures().filter(
    (feature) => labelLayers[feature.layer.id],
  )
  const renderedDormitoryZones = renderedLabelFeatures.filter(
    (feature) => feature.layer.id === 'dormitory-zone-labels',
  )
  const renderedCoreLabels = renderedLabelFeatures.filter(
    (feature) => feature.layer.id === 'core-campus-labels',
  )
  return {
    apiFeatureCount: data.features.length,
    apiFeatureTypes: summarizeFeatureTypes(data),
    sourceExists: Boolean(map.getSource(CAMPUS_SOURCE_ID)),
    sourceLoaded: map.isSourceLoaded(CAMPUS_SOURCE_ID),
    sourceFeatureCount: data.features.length,
    renderedFeatureCount: renderedFeatures.length,
    renderedFeatureTypes: countValues(renderedFeatures.map(
      (feature) => String(feature.properties?.featureType ?? 'UNKNOWN'),
    )),
    renderedLayers: countValues(renderedFeatures.map((feature) => feature.layer.id)),
    visualLayers,
    labelLayers,
    dormitoryZoneSourceFeatureCount: data.features.filter(
      (feature) => feature.properties.featureType === 'DORMITORY_ZONE',
    ).length,
    renderedDormitoryZoneLabelCount: renderedDormitoryZones.length,
    renderedCoreCampusLabelNames: [...new Set(renderedCoreLabels
      .map((feature) => String(feature.properties?.displayName ?? feature.properties?.name ?? ''))
      .filter((name) => CORE_CAMPUS_LABELS.includes(name)))],
    center: { longitude: center.lng, latitude: center.lat },
    zoom: map.getZoom(),
    canvas: { width: canvasBounds.width, height: canvasBounds.height },
  }
}

export function installDevelopmentDiagnostics(
  map: Map,
  data: NormalizedFeatureCollection,
): void {
  window.__NJUPT_CAMPUS_MAP__ = map
  const canvas = map.getCanvas()
  const update = () => {
    const diagnostics = captureRenderDiagnostics(map, data)
    window.__NJUPT_MAP_DIAGNOSTICS__ = diagnostics
    canvas.dataset.sourceFeatureCount = String(diagnostics.sourceFeatureCount)
    canvas.dataset.renderedFeatureCount = String(diagnostics.renderedFeatureCount)
    canvas.dataset.dormitoryZoneSourceFeatureCount = String(
      diagnostics.dormitoryZoneSourceFeatureCount,
    )
    canvas.dataset.renderedDormitoryZoneLabelCount = String(
      diagnostics.renderedDormitoryZoneLabelCount,
    )
    canvas.dataset.mapZoom = diagnostics.zoom.toFixed(3)
    canvas.dataset.renderedCoreCampusLabelNames = JSON.stringify(
      diagnostics.renderedCoreCampusLabelNames,
    )
    console.info('[NJUPT Map] render diagnostics', JSON.stringify(diagnostics))
    if (diagnostics.apiFeatureCount > 0
      && diagnostics.sourceLoaded
      && diagnostics.renderedFeatureCount === 0) {
      console.warn('[NJUPT Map] Map loaded but no campus features are currently rendered.')
    }
  }
  map.on('idle', update)
  map.once('idle', () => window.setTimeout(update, 500))
  map.on('styledata', () => window.setTimeout(update, 500))
  const onSourceData = (event: { sourceId?: string; isSourceLoaded?: boolean }) => {
    if (event.sourceId !== CAMPUS_SOURCE_ID || !event.isSourceLoaded) return
    map.off('sourcedata', onSourceData)
    requestAnimationFrame(update)
  }
  map.on('sourcedata', onSourceData)
}

export function isMapDiagnosticsEnabled(search = window.location.search): boolean {
  return import.meta.env.DEV || new URLSearchParams(search).get('mapDiagnostics') === '1'
}

export function applyRequestedDiagnosticZoom(map: Map, search = window.location.search): void {
  const rawZoom = new URLSearchParams(search).get('mapZoom')
  if (rawZoom === null) return
  const zoom = Number(rawZoom)
  if (!Number.isFinite(zoom) || zoom < 14 || zoom > 20) return
  map.setMaxBounds(null)
  map.jumpTo({ zoom })
}

export async function runRequestedDiagnosticZoomSweep(
  map: Map,
  data: NormalizedFeatureCollection,
  search = window.location.search,
): Promise<void> {
  if (new URLSearchParams(search).get('mapZoomSweep') !== '1') return
  map.setMaxBounds(null)
  const results = []
  for (const zoom of [15, 15.2, 15.5, 16, 16.5, 17]) {
    map.jumpTo({ zoom })
    await new Promise<void>((resolve) => map.once('idle', () => resolve()))
    const diagnostics = captureRenderDiagnostics(map, data)
    results.push({
      zoom: Number(diagnostics.zoom.toFixed(3)),
      sourceZoneCount: diagnostics.dormitoryZoneSourceFeatureCount,
      renderedZoneCount: diagnostics.renderedDormitoryZoneLabelCount,
      renderedCoreLabels: diagnostics.renderedCoreCampusLabelNames,
    })
  }
  map.getCanvas().dataset.zoomSweep = JSON.stringify(results)
}

function countValues(values: string[]): Record<string, number> {
  return values.reduce<Record<string, number>>((summary, value) => {
    summary[value] = (summary[value] ?? 0) + 1
    return summary
  }, {})
}
