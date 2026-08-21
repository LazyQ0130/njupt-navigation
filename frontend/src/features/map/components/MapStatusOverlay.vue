<script setup lang="ts">
import type { MapUiState } from '../mapUiState'

defineProps<{ state: MapUiState; message: string }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <div v-if="state !== 'ready'" class="status-overlay" :role="state === 'error' ? 'alert' : 'status'">
    <div class="status-card">
      <span v-if="state === 'loading'" class="loader" aria-hidden="true" />
      <span v-else class="status-icon" aria-hidden="true">{{ state === 'error' ? '!' : '○' }}</span>
      <h2>{{ state === 'loading' ? '正在绘制校园' : state === 'error' ? '地图暂时无法加载' : '暂无地图数据' }}</h2>
      <p>{{ message }}</p>
      <button v-if="state === 'error'" type="button" @click="$emit('retry')">重新加载</button>
    </div>
  </div>
</template>

<style scoped>
.status-overlay { position: absolute; z-index: 15; inset: 0; display: grid; place-items: center; padding: 24px; background: rgb(235 240 233 / 80%); backdrop-filter: blur(6px); }
.status-card { width: min(360px, 100%); border: 1px solid rgb(255 255 255 / 85%); border-radius: 24px; background: rgb(255 255 255 / 94%); padding: 28px; box-shadow: 0 20px 50px rgb(38 60 48 / 16%); text-align: center; }
.loader, .status-icon { display: grid; width: 42px; height: 42px; margin: 0 auto 16px; place-items: center; border-radius: 50%; }
.loader { border: 3px solid #d5e1d9; border-top-color: #2e7057; animation: spin .9s linear infinite; }
.status-icon { background: #edf3ee; color: #365a4a; font-weight: 800; }
h2 { margin: 0; color: #1f342b; font-size: 18px; }
p { margin: 8px 0 0; color: #66736d; font-size: 13px; line-height: 1.6; }
button { margin-top: 18px; border: 0; border-radius: 12px; background: #275f4b; padding: 10px 18px; color: white; font-weight: 700; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
