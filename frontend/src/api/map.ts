import { http } from './http'

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
  data: {
    buildings: number
    pois: number
  }
}

export interface MapBootstrapResponse {
  schemaVersion: string
  campuses: CampusSummary[]
}

export async function fetchMapBootstrap(): Promise<MapBootstrapResponse> {
  const response = await http.get<MapBootstrapResponse>('/map/bootstrap')
  return response.data
}

