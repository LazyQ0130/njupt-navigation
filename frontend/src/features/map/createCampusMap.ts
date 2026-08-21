import booleanPointInPolygon from '@turf/boolean-point-in-polygon'
import { point } from '@turf/helpers'
import {
  AttributionControl,
  GeoJSONSource,
  Map,
  type MapLayerMouseEvent,
} from 'maplibre-gl'
import type { Feature, Point } from 'geojson'
import { campusLabelLayers, campusVisualLayers } from './layers'
import { MAP_PALETTE } from './mapPalette'
import {
  BUILDING_EXTRUSION_LAYER_ID,
  CAMPUS_ATTRIBUTION,
  CAMPUS_SOURCE_ID,
  USER_LOCATION_SOURCE_ID,
  createMapOptions,
} from './mapConfig'
import type { CampusBoundaryFeature, CampusMapController, CampusMapInput } from './types'
import { addGisReviewLayers, setReviewLayerVisibility as setGisReviewLayerVisibility } from './reviewLayers'
import { installDevelopmentDiagnostics } from './renderDiagnostics'
import { campusFitPadding, deriveCampusViewport } from './campusViewport'

export function createCampusMap(input: CampusMapInput): CampusMapController {
  const { container, campus, data, reviewData, callbacks } = input
  const viewport = deriveCampusViewport(data, campus)
  const initialBounds = viewport.bounds
  const map = new Map(createMapOptions(container, campus, viewport))
  let selectedBuildingId: string | number | undefined
  let destroyed = false

  const usesOsm = data.features.some((feature) => feature.properties.dataSource === 'OPENSTREETMAP')
  const attribution = usesOsm
    ? '<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">© OpenStreetMap contributors</a> · MapLibre'
    : CAMPUS_ATTRIBUTION
  map.addControl(new AttributionControl({ compact: true, customAttribution: attribution }), 'bottom-right')

  map.once('load', () => {
    if (destroyed) return
    map.addSource(CAMPUS_SOURCE_ID, {
      type: 'geojson',
      data,
    })
    campusVisualLayers.forEach((layer) => map.addLayer(layer))
    if (reviewData) addGisReviewLayers(map, reviewData, callbacks.onReviewSelect)
    addUserLocationLayer(map)
    fitCampus(map, initialBounds, campus, false)
    configureBuildingInteraction(map, (id, name, category) => {
      if (selectedBuildingId !== undefined) {
        map.setFeatureState({ source: CAMPUS_SOURCE_ID, id: selectedBuildingId }, { selected: false })
      }
      selectedBuildingId = id
      map.setFeatureState({ source: CAMPUS_SOURCE_ID, id }, { selected: true })
      callbacks.onBuildingSelect({ name, category })
    })
    const canvas = map.getCanvas()
    canvas.setAttribute('role', 'img')
    canvas.setAttribute('aria-label', `${campus.name} 2.5D 交互地图`)
    map.once('idle', () => {
      if (destroyed) return
      campusLabelLayers.forEach((layer) => map.addLayer(layer))
    })
    if (import.meta.env.DEV) installDevelopmentDiagnostics(map, data)
    requestAnimationFrame(() => {
      if (destroyed) return
      map.resize()
      fitCampus(map, initialBounds, campus, false)
    })
    callbacks.onReady()
  })

  map.on('error', (event) => {
    if (!destroyed && event.error) callbacks.onError(event.error.message)
  })

  const resizeObserver = new ResizeObserver(() => map.resize())
  resizeObserver.observe(container)

  return {
    destroy() {
      destroyed = true
      resizeObserver.disconnect()
      map.remove()
    },
    resize() {
      map.resize()
    },
    reset() {
      map.setMaxBounds(initialBounds)
      fitCampus(map, initialBounds, campus, true)
    },
    resetNorth() {
      map.easeTo({ bearing: 0, pitch: campus.camera.pitch, duration: 200 })
    },
    isInsideCampus(longitude, latitude) {
      const boundary = data.features.find(
        (feature) => feature.properties.featureType === 'CAMPUS_BOUNDARY',
      ) as CampusBoundaryFeature | undefined
      if (boundary) return booleanPointInPolygon(point([longitude, latitude]), boundary)
      return longitude >= campus.bounds.west && longitude <= campus.bounds.east
        && latitude >= campus.bounds.south && latitude <= campus.bounds.north
    },
    showLocation(longitude, latitude, allowOutside) {
      if (allowOutside) map.setMaxBounds(null)
      else map.setMaxBounds(initialBounds)
      const source = map.getSource(USER_LOCATION_SOURCE_ID) as GeoJSONSource | undefined
      source?.setData(userLocationFeature(longitude, latitude))
      map.flyTo({ center: [longitude, latitude], zoom: 17.5, pitch: 42, essential: true })
    },
    setReviewLayerVisibility(group, visible) {
      setGisReviewLayerVisibility(map, group, visible)
    },
  }
}

function fitCampus(
  map: Map,
  bounds: [[number, number], [number, number]],
  campus: CampusMapInput['campus'],
  animate: boolean,
): void {
  map.fitBounds(bounds, {
    padding: campusFitPadding(map.getContainer().getBoundingClientRect().width),
    pitch: campus.camera.pitch,
    bearing: campus.camera.bearing,
    duration: animate ? 600 : 0,
    essential: true,
  })
}

function addUserLocationLayer(map: Map): void {
  map.addSource(USER_LOCATION_SOURCE_ID, {
    type: 'geojson',
    data: userLocationFeature(0, 0),
  })
  map.addLayer({
    id: 'user-location-halo',
    type: 'circle',
    source: USER_LOCATION_SOURCE_ID,
    paint: {
      'circle-radius': 13,
      'circle-color': MAP_PALETTE.location,
      'circle-opacity': 0.18,
    },
  })
  map.addLayer({
    id: 'user-location-dot',
    type: 'circle',
    source: USER_LOCATION_SOURCE_ID,
    paint: {
      'circle-radius': 6,
      'circle-color': MAP_PALETTE.location,
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 2.5,
    },
  })
}

function configureBuildingInteraction(
  map: Map,
  onSelect: (id: string | number, name: string, category: string) => void,
): void {
  map.on('mouseenter', BUILDING_EXTRUSION_LAYER_ID, () => {
    map.getCanvas().style.cursor = 'pointer'
  })
  map.on('mouseleave', BUILDING_EXTRUSION_LAYER_ID, () => {
    map.getCanvas().style.cursor = ''
  })
  map.on('click', BUILDING_EXTRUSION_LAYER_ID, (event: MapLayerMouseEvent) => {
    const feature = event.features?.[0]
    if (!feature || feature.id === undefined) return
    onSelect(
      feature.id,
      String(feature.properties?.name ?? '未命名建筑'),
      String(feature.properties?.category ?? 'BUILDING'),
    )
  })
}

function userLocationFeature(longitude: number, latitude: number): Feature<Point> {
  return {
    type: 'Feature',
    properties: {},
    geometry: { type: 'Point', coordinates: [longitude, latitude] },
  }
}
