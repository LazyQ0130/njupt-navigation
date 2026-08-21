import type { Feature, FeatureCollection, Geometry, MultiPolygon, Polygon } from 'geojson'
import type { CampusFeatureProperties, CampusSummary } from '@/api/map'

export const SUPPORTED_FEATURE_TYPES = [
  'CAMPUS_BOUNDARY',
  'GREEN',
  'WATER',
  'SPORT',
  'PLAZA',
  'ROAD_MAIN',
  'ROAD_PEDESTRIAN',
  'BUILDING',
  'POI',
] as const

export type SupportedFeatureType = (typeof SUPPORTED_FEATURE_TYPES)[number]

export type NormalizedCampusFeature = Feature<Geometry, CampusFeatureProperties>
export type NormalizedFeatureCollection = FeatureCollection<Geometry, CampusFeatureProperties>
export type CampusBoundaryFeature = Feature<Polygon | MultiPolygon, CampusFeatureProperties>

export interface SelectedPlace {
  name: string
  category: string
}

export interface CampusMapController {
  destroy: () => void
  reset: () => void
  resetNorth: () => void
  resize: () => void
  isInsideCampus: (longitude: number, latitude: number) => boolean
  showLocation: (longitude: number, latitude: number, allowOutside: boolean) => void
}

export interface CampusMapCallbacks {
  onBuildingSelect: (place: SelectedPlace) => void
  onError: (message: string) => void
  onReady: () => void
}

export interface CampusMapInput {
  container: HTMLElement
  campus: CampusSummary
  data: NormalizedFeatureCollection
  callbacks: CampusMapCallbacks
}
