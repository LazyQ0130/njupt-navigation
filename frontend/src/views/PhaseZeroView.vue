<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useMapBootstrapStore } from '@/stores/mapBootstrap'

const store = useMapBootstrapStore()
const campus = computed(() => store.campuses[0])

onMounted(() => store.load())
</script>

<template>
  <main class="relative flex min-h-dvh items-center justify-center overflow-hidden bg-slate-100 px-5 py-10">
    <div class="absolute inset-0 opacity-60" aria-hidden="true">
      <div class="grid-pattern h-full w-full" />
    </div>

    <section class="relative w-full max-w-lg overflow-hidden rounded-3xl border border-white/70 bg-white/90 shadow-2xl shadow-njupt-950/10 backdrop-blur">
      <div class="bg-gradient-to-br from-njupt-700 to-njupt-950 px-6 py-7 text-white">
        <div class="mb-8 flex items-center justify-between">
          <span class="rounded-full bg-white/15 px-3 py-1 text-xs font-semibold tracking-wide">PHASE 0</span>
          <span class="flex items-center gap-2 text-xs text-blue-100">
            <span class="h-2 w-2 rounded-full bg-emerald-300" />
            工程基础已就绪
          </span>
        </div>
        <p class="text-sm font-medium text-blue-100">NJUPT Xianlin Smart Campus Map</p>
        <h1 class="mt-2 text-3xl font-bold leading-tight">南邮仙林智慧校园导航</h1>
        <p class="mt-3 max-w-md text-sm leading-6 text-blue-100">
          当前版本完成工程、PostGIS 数据模型与导入能力。2.5D 地图将在 Phase 1 接入真实校园数据后呈现。
        </p>
      </div>

      <div class="space-y-5 p-6">
        <div v-if="store.loading" class="rounded-2xl bg-slate-50 p-5 text-sm text-slate-600" role="status">
          正在连接校园地图数据服务…
        </div>

        <div v-else-if="store.error" class="rounded-2xl border border-rose-200 bg-rose-50 p-5" role="alert">
          <p class="font-semibold text-rose-900">基础数据暂不可用</p>
          <p class="mt-1 text-sm text-rose-700">{{ store.error }}</p>
          <button class="mt-4 rounded-xl bg-rose-700 px-4 py-2 text-sm font-semibold text-white" @click="store.load">
            重新连接
          </button>
        </div>

        <div v-else-if="campus" class="space-y-4">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-widest text-njupt-700">默认校区</p>
              <h2 class="mt-1 text-xl font-bold text-slate-900">{{ campus.name }}</h2>
            </div>
            <span class="rounded-xl bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">API 正常</span>
          </div>

          <dl class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl bg-slate-50 p-4">
              <dt class="text-xs text-slate-500">建筑数据</dt>
              <dd class="mt-1 text-2xl font-bold text-slate-900">{{ campus.data.buildings }}</dd>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <dt class="text-xs text-slate-500">POI 数据</dt>
              <dd class="mt-1 text-2xl font-bold text-slate-900">{{ campus.data.pois }}</dd>
            </div>
          </dl>
        </div>

        <div class="border-t border-slate-100 pt-5">
          <p class="text-xs leading-5 text-slate-500">
            下一步需要核验建筑轮廓、入口、道路、绿地和水体。当前示例数据仅用于验证导入流程。
          </p>
        </div>
      </div>
    </section>
  </main>
</template>

