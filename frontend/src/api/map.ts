import { http } from './http'
import type { FeatureCollection, Geometry } from 'geojson'
import type { GisReviewCollections, GisReviewLayerKey } from '@/features/map/gisReview'

export interface CameraConfig {
  longitude: number
  latitude: number
  zoom: number
  pitch: number
  bearing: number
}

export interface CampusSummary {
  id: string
  code: string
  name: string
  officialName?: string
  displayName?: string
  aliases?: string[]
  keywords?: string[]
  labelVisible?: boolean
  buildingId?: string
  camera: CameraConfig
  bounds: {
    west: number
    south: number
    east: number
    north: number
  }
  data: {
    buildings: number
    pois: number
    mapFeatures: number
  }
  layers: {
    buildings: boolean
    ground: boolean
    roads: boolean
    pois: boolean
  }
}

export interface CampusFeatureProperties {
  id: string
  featureType: string
  name: string
  category?: string
  color?: string
  height?: number
  minHeight?: number
  priority?: number
  dataSource?: string
  verificationStatus?: string
  sourceId?: string
  sourceUpdatedAt?: string
  heightSource?: string
}

export type CampusFeatureCollection = FeatureCollection<Geometry, CampusFeatureProperties> & {
  schemaVersion?: string
  campusCode?: string
}

export interface MapBootstrapResponse {
  schemaVersion: string
  campuses: CampusSummary[]
}

export async function fetchMapBootstrap(): Promise<MapBootstrapResponse> {
  const response = await http.get<MapBootstrapResponse>('/map/bootstrap')
  return response.data
}

export async function fetchMapFeatures(campusCode: string): Promise<CampusFeatureCollection> {
  const response = await http.get<CampusFeatureCollection>('/map/features', {
    params: { campusCode },
  })
  return response.data
}

export async function fetchGisReviewLayers(keys: GisReviewLayerKey[]): Promise<GisReviewCollections> {
  const entries = await Promise.all(keys.map(async (key) => {
    const response = await http.get<FeatureCollection<Geometry>>(`/map/review/${key}`)
    return [key, response.data] as const
  }))
  return Object.fromEntries(entries) as GisReviewCollections
}
