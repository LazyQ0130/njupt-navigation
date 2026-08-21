import type { Map } from 'maplibre-gl'
import type { NormalizedFeatureCollection } from './types'
import { CAMPUS_SOURCE_ID } from './mapConfig'
import { campusVisualLayers } from './layers'

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
  return {
    apiFeatureCount: data.features.length,
    apiFeatureTypes: summarizeFeatureTypes(data),
    sourceExists: Boolean(map.getSource(CAMPUS_SOURCE_ID)),
    sourceLoaded: map.isSourceLoaded(CAMPUS_SOURCE_ID),
    sourceFeatureCount: map.querySourceFeatures(CAMPUS_SOURCE_ID).length,
    renderedFeatureCount: renderedFeatures.length,
    renderedFeatureTypes: countValues(renderedFeatures.map(
      (feature) => String(feature.properties?.featureType ?? 'UNKNOWN'),
    )),
    renderedLayers: countValues(renderedFeatures.map((feature) => feature.layer.id)),
    visualLayers,
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
  const update = () => {
    const diagnostics = captureRenderDiagnostics(map, data)
    window.__NJUPT_MAP_DIAGNOSTICS__ = diagnostics
    const canvas = map.getCanvas()
    canvas.dataset.sourceFeatureCount = String(diagnostics.sourceFeatureCount)
    canvas.dataset.renderedFeatureCount = String(diagnostics.renderedFeatureCount)
    console.info('[NJUPT Map] render diagnostics', JSON.stringify(diagnostics))
    if (diagnostics.apiFeatureCount > 0
      && diagnostics.sourceLoaded
      && diagnostics.renderedFeatureCount === 0) {
      console.warn('[NJUPT Map] Map loaded but no campus features are currently rendered.')
    }
  }
  map.once('idle', update)
  map.once('render', () => requestAnimationFrame(update))
  const onSourceData = (event: { sourceId?: string; isSourceLoaded?: boolean }) => {
    if (event.sourceId !== CAMPUS_SOURCE_ID || !event.isSourceLoaded) return
    map.off('sourcedata', onSourceData)
    requestAnimationFrame(update)
  }
  map.on('sourcedata', onSourceData)
}

function countValues(values: string[]): Record<string, number> {
  return values.reduce<Record<string, number>>((summary, value) => {
    summary[value] = (summary[value] ?? 0) + 1
    return summary
  }, {})
}
