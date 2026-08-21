import { defineStore } from 'pinia'
import { fetchMapBootstrap, type CampusSummary } from '@/api/map'
import { formatApiError } from '@/api/http'

export const useMapBootstrapStore = defineStore('map-bootstrap', {
  state: () => ({
    campuses: [] as CampusSummary[],
    schemaVersion: '',
    loading: false,
    error: '',
  }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        const response = await fetchMapBootstrap()
        this.campuses = response.campuses
        this.schemaVersion = response.schemaVersion
      } catch (error) {
        this.error = formatApiError(error)
      } finally {
        this.loading = false
      }
    },
  },
})

