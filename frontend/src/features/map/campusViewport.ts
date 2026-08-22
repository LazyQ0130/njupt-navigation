import type { CampusSummary } from '@/api/map'
import type { NormalizedFeatureCollection } from './types'

export type CampusBoundsTuple = [[number, number], [number, number]]

export interface CampusViewport {
  bounds: CampusBoundsTuple
  center: [number, number]
  derivedFromBoundary: boolean
}

export function deriveCampusViewport(
  data: NormalizedFeatureCollection,
  campus: CampusSummary,
): CampusViewport {
  const extent = data.features
    .filter((feature) => feature.properties.featureType === 'CAMPUS_BOUNDARY')
    .reduce<Extent | undefined>((current, feature) => {
      if (feature.geometry.type !== 'Polygon' && feature.geometry.type !== 'MultiPolygon') {
        return current
      }
      return extendCoordinates(current, feature.geometry.coordinates)
    }, undefined)

  if (extent && extent.west < extent.east && extent.south < extent.north) {
    const bounds: CampusBoundsTuple = [
      [extent.west, extent.south],
      [extent.east, extent.north],
    ]
    return {
      bounds,
      center: [(extent.west + extent.east) / 2, (extent.south + extent.north) / 2],
      derivedFromBoundary: true,
    }
  }

  return {
    bounds: [
      [campus.bounds.west, campus.bounds.south],
      [campus.bounds.east, campus.bounds.north],
    ],
    center: [campus.camera.longitude, campus.camera.latitude],
    derivedFromBoundary: false,
  }
}

export function campusFitPadding(width: number) {
  return width < 640
    ? { top: 80, right: 28, bottom: 112, left: 28 }
    : { top: 96, right: 96, bottom: 112, left: 96 }
}

interface Extent {
  west: number
  south: number
  east: number
  north: number
}

function extendCoordinates(current: Extent | undefined, value: unknown): Extent | undefined {
  if (!Array.isArray(value)) return current
  if (value.length >= 2 && typeof value[0] === 'number' && typeof value[1] === 'number') {
    const longitude = value[0]
    const latitude = value[1]
    if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) return current
    if (longitude < -180 || longitude > 180 || latitude < -90 || latitude > 90) return current
    return {
      west: Math.min(current?.west ?? longitude, longitude),
      south: Math.min(current?.south ?? latitude, latitude),
      east: Math.max(current?.east ?? longitude, longitude),
      north: Math.max(current?.north ?? latitude, latitude),
    }
  }
  return value.reduce<Extent | undefined>(extendCoordinates, current)
}
