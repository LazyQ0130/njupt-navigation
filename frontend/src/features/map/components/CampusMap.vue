<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import type { CampusSummary } from '@/api/map'
import { fetchMapFeatures } from '@/api/map'
import { formatApiError } from '@/api/http'
import { useMapBootstrapStore } from '@/stores/mapBootstrap'
import { createCampusMap } from '../createCampusMap'
import { normalizeMapData } from '../mapDataMapper'
import { deriveMapUiState, geolocationErrorMessage } from '../mapUiState'
import type { CampusMapController, NormalizedFeatureCollection } from '../types'
import MapControls from './MapControls.vue'
import MapSearchPlaceholder from './MapSearchPlaceholder.vue'
import MapStatusOverlay from './MapStatusOverlay.vue'
import MapToast from './MapToast.vue'
import QuickActions from './QuickActions.vue'

const bootstrap = useMapBootstrapStore()
const mapHost = ref<HTMLElement>()
const campus = shallowRef<CampusSummary>()
const data = shallowRef<NormalizedFeatureCollection>({ type: 'FeatureCollection', features: [] })
const loading = ref(true)
const error = ref('')
const locating = ref(false)
const selectedBuilding = ref('')
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
  selectedBuilding.value = ''
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
        onBuildingSelect: (name) => { selectedBuilding.value = name },
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
  selectedBuilding.value = ''
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
      <div class="brand-row">
        <div class="brand-mark" aria-hidden="true">邮</div>
        <div>
          <p>NJUPT SMART CAMPUS</p>
          <h1>{{ campus?.name ?? '南邮仙林智慧校园' }}</h1>
        </div>
        <span class="demo-badge">合成演示数据</span>
      </div>
      <MapSearchPlaceholder @activate="showToast('地点搜索将在 Phase 2 开放，本阶段专注地图浏览。')" />
      <QuickActions @choose="(label) => showToast(`${label}分类筛选将在后续阶段开放。`)" />
    </header>

    <aside class="map-controls">
      <MapControls :locating="locating" :disabled="uiState !== 'ready'" @locate="requestLocation" @reset="resetCampus" />
    </aside>

    <div v-if="selectedBuilding" class="building-card" role="status">
      <span>已选择建筑</span>
      <strong>{{ selectedBuilding }}</strong>
      <button type="button" aria-label="关闭建筑信息" @click="selectedBuilding = ''">×</button>
    </div>

    <div class="toast-slot">
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
.map-page { position: relative; width: 100%; height: 100dvh; min-height: 520px; overflow: hidden; background: #e9eee7; }
.map-canvas { position: absolute; inset: 0; }
.map-header { position: absolute; z-index: 10; top: 0; left: 0; display: grid; gap: 11px; padding: max(14px, env(safe-area-inset-top)) 16px 0 max(16px, env(safe-area-inset-left)); pointer-events: none; }
.map-header > * { pointer-events: auto; }
.brand-row { display: flex; width: min(560px, calc(100vw - 32px)); align-items: center; gap: 10px; }
.brand-mark { display: grid; width: 38px; height: 38px; flex: 0 0 auto; place-items: center; border-radius: 12px; background: #264f40; color: white; box-shadow: 0 8px 20px rgb(33 68 54 / 20%); font-family: serif; font-weight: 800; }
.brand-row p { margin: 0; color: #50665c; font-size: 9px; font-weight: 800; letter-spacing: .14em; }
.brand-row h1 { margin: 2px 0 0; color: #1c342a; font-size: 15px; line-height: 1.2; }
.demo-badge { margin-left: auto; border: 1px solid rgb(255 255 255 / 70%); border-radius: 999px; background: rgb(255 255 255 / 82%); padding: 6px 9px; color: #8a5d24; font-size: 10px; font-weight: 750; backdrop-filter: blur(10px); }
.map-controls { position: absolute; z-index: 11; right: max(12px, env(safe-area-inset-right)); bottom: max(90px, calc(env(safe-area-inset-bottom) + 70px)); }
.building-card { position: absolute; z-index: 11; left: max(16px, env(safe-area-inset-left)); bottom: max(22px, calc(env(safe-area-inset-bottom) + 14px)); display: grid; min-width: min(300px, calc(100vw - 90px)); border: 1px solid rgb(255 255 255 / 75%); border-radius: 17px; background: rgb(255 255 255 / 93%); padding: 12px 42px 12px 15px; box-shadow: 0 12px 30px rgb(28 55 43 / 18%); backdrop-filter: blur(12px); }
.building-card span { color: #738178; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
.building-card strong { margin-top: 2px; color: #263b31; font-size: 15px; }
.building-card button { position: absolute; top: 8px; right: 8px; width: 30px; height: 30px; border: 0; background: transparent; color: #687970; font-size: 20px; }
.toast-slot { position: absolute; z-index: 20; bottom: max(20px, calc(env(safe-area-inset-bottom) + 14px)); left: 50%; transform: translateX(-50%); }
@media (min-width: 768px) {
  .map-header { padding: 22px 0 0 24px; }
  .map-controls { right: 22px; bottom: 108px; }
  .brand-row h1 { font-size: 17px; }
}
</style>
