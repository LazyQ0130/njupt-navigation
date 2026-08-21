<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import type { CampusSummary } from '@/api/map'
import { fetchMapFeatures } from '@/api/map'
import { formatApiError } from '@/api/http'
import { useMapBootstrapStore } from '@/stores/mapBootstrap'
import { createCampusMap } from '../createCampusMap'
import { normalizeMapData } from '../mapDataMapper'
import { deriveMapUiState, geolocationErrorMessage } from '../mapUiState'
import type { CampusMapController, NormalizedFeatureCollection, SelectedPlace } from '../types'
import MapControls from './MapControls.vue'
import MapSearchPlaceholder from './MapSearchPlaceholder.vue'
import MapStatusOverlay from './MapStatusOverlay.vue'
import MapToast from './MapToast.vue'
import PlacePeek from './PlacePeek.vue'
import QuickActions from './QuickActions.vue'

const bootstrap = useMapBootstrapStore()
const mapHost = ref<HTMLElement>()
const campus = shallowRef<CampusSummary>()
const data = shallowRef<NormalizedFeatureCollection>({ type: 'FeatureCollection', features: [] })
const loading = ref(true)
const error = ref('')
const locating = ref(false)
const selectedPlace = ref<SelectedPlace>()
const toastMessage = ref('')
const toastActionLabel = ref('')
const toastSecondaryLabel = ref('')
let toastAction: (() => void) | undefined
let toastSecondaryAction: (() => void) | undefined
let toastTimer: ReturnType<typeof setTimeout> | undefined
let controller: CampusMapController | undefined

const uiState = computed(() => deriveMapUiState(loading.value, error.value, data.value.features.length))

async function loadMap(): Promise<void> {
  loading.value = true
  error.value = ''
  selectedPlace.value = undefined
  controller?.destroy()
  controller = undefined
  try {
    await bootstrap.load()
    if (bootstrap.error) throw new Error(bootstrap.error)
    campus.value = bootstrap.campuses[0]
    if (!campus.value) {
      data.value = { type: 'FeatureCollection', features: [] }
      loading.value = false
      return
    }
    data.value = normalizeMapData(await fetchMapFeatures(campus.value.code))
    if (data.value.features.length === 0) {
      loading.value = false
      return
    }
    await nextTick()
    if (!mapHost.value) throw new Error('地图容器尚未准备好')
    controller = createCampusMap({
      container: mapHost.value,
      campus: campus.value,
      data: data.value,
      callbacks: {
        onBuildingSelect: (place) => { selectedPlace.value = place },
        onError: (message) => showToast(`地图资源提示：${message}`),
        onReady: () => { loading.value = false },
      },
    })
  } catch (reason) {
    loading.value = false
    error.value = formatApiError(reason)
  }
}

function requestLocation(): void {
  if (!controller || !navigator.geolocation) {
    showToast('当前浏览器或环境不支持定位，请使用校园默认视角。')
    return
  }
  locating.value = true
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      locating.value = false
      const { longitude, latitude } = coords
      if (controller?.isInsideCampus(longitude, latitude)) {
        controller.showLocation(longitude, latitude, false)
        showToast('已定位到校园范围内的当前位置。')
        return
      }
      showToast(
        '当前位置在演示校园范围外。可临时查看位置，或返回校园默认视角。',
        '查看我的位置',
        () => controller?.showLocation(longitude, latitude, true),
        '返回校园',
        resetCampus,
      )
    },
    (locationError) => {
      locating.value = false
      showToast(geolocationErrorMessage(locationError.code))
    },
    { enableHighAccuracy: true, timeout: 10_000, maximumAge: 30_000 },
  )
}

function resetCampus(): void {
  controller?.reset()
  selectedPlace.value = undefined
}

function resetNorth(): void {
  controller?.resetNorth()
}

function showToast(
  message: string,
  actionLabel = '',
  action?: () => void,
  secondaryLabel = '',
  secondary?: () => void,
): void {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = message
  toastActionLabel.value = actionLabel
  toastSecondaryLabel.value = secondaryLabel
  toastAction = action
  toastSecondaryAction = secondary
  if (!actionLabel && !secondaryLabel) toastTimer = setTimeout(closeToast, 4200)
}

function closeToast(): void {
  toastMessage.value = ''
  toastActionLabel.value = ''
  toastSecondaryLabel.value = ''
  toastAction = undefined
  toastSecondaryAction = undefined
}

function runToastAction(): void {
  toastAction?.()
  closeToast()
}

function runToastSecondary(): void {
  toastSecondaryAction?.()
  closeToast()
}

onMounted(loadMap)
onBeforeUnmount(() => {
  if (toastTimer) clearTimeout(toastTimer)
  controller?.destroy()
})
</script>

<template>
  <main class="map-page">
    <div ref="mapHost" class="map-canvas" />

    <header class="map-header">
      <h1 class="sr-only">{{ campus?.name ?? '南邮仙林智慧校园' }}</h1>
      <MapSearchPlaceholder @activate="showToast('搜索将在 Phase 2 开放')" />
    </header>

    <nav class="quick-actions" aria-label="校园地图快捷入口">
      <QuickActions @choose="(label) => showToast(`${label}将在 Phase 2 开放`)" />
    </nav>

    <aside class="map-controls" :class="{ 'has-place': selectedPlace }">
      <MapControls
        :locating="locating"
        :disabled="uiState !== 'ready'"
        @locate="requestLocation"
        @compass="resetNorth"
        @reset="resetCampus"
      />
    </aside>

    <div v-if="selectedPlace" class="place-slot">
      <PlacePeek :place="selectedPlace" @close="selectedPlace = undefined" />
    </div>

    <div class="toast-slot" :class="{ 'has-place': selectedPlace }">
      <MapToast
        :message="toastMessage"
        :action-label="toastActionLabel"
        :secondary-label="toastSecondaryLabel"
        @action="runToastAction"
        @secondary="runToastSecondary"
        @close="closeToast"
      />
    </div>

    <MapStatusOverlay
      :state="uiState"
      :message="error || (uiState === 'empty' ? '当前校区没有可显示的地图要素，请先导入 GeoJSON 数据。' : '正在获取建筑、道路与地表数据…')"
      @retry="loadMap"
    />
  </main>
</template>

<style scoped>
.map-page { position: relative; width: 100%; height: 100dvh; min-height: 520px; overflow: hidden; background: #f3f1ec; }
.map-canvas { position: absolute; inset: 0; }
.map-header { position: absolute; z-index: 10; top: 0; left: 0; padding: max(12px, env(safe-area-inset-top)) 12px 0 max(12px, env(safe-area-inset-left)); pointer-events: none; }
.map-header > * { pointer-events: auto; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0, 0, 0, 0); clip-path: inset(50%); white-space: nowrap; }
.quick-actions { position: absolute; z-index: 12; bottom: max(10px, env(safe-area-inset-bottom)); left: 50%; transform: translateX(-50%); }
.map-controls { position: absolute; z-index: 11; right: max(12px, env(safe-area-inset-right)); bottom: max(86px, calc(env(safe-area-inset-bottom) + 78px)); transition: bottom var(--ui-motion); }
.map-controls.has-place { bottom: max(196px, calc(env(safe-area-inset-bottom) + 188px)); }
.place-slot { position: absolute; z-index: 13; right: 12px; bottom: max(112px, calc(env(safe-area-inset-bottom) + 104px)); left: 12px; display: flex; justify-content: center; pointer-events: none; }
.place-slot > * { pointer-events: auto; }
.toast-slot { position: absolute; z-index: 20; top: max(74px, calc(env(safe-area-inset-top) + 66px)); left: 50%; transform: translateX(-50%); }
@media (min-width: 768px) {
  .map-header { padding: 24px 0 0 24px; }
  .quick-actions { bottom: 18px; }
  .map-controls, .map-controls.has-place { top: 24px; right: 24px; bottom: auto; }
  .place-slot { right: auto; bottom: 24px; left: 24px; justify-content: flex-start; }
  .toast-slot, .toast-slot.has-place { top: 86px; bottom: auto; }
}
</style>
