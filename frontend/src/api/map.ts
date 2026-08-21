import { http } from './http'
import type { FeatureCollection, Geometry } from 'geojson'

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
