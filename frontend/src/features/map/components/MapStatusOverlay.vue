<script setup lang="ts">
import { CircleAlert, Database } from '@lucide/vue'
import type { MapUiState } from '../mapUiState'

defineProps<{ state: MapUiState; message: string }>()
defineEmits<{ retry: [] }>()
</script>

<template>
  <div v-if="state !== 'ready'" class="status-overlay" :role="state === 'error' ? 'alert' : 'status'">
    <div class="status-card">
      <span v-if="state === 'loading'" class="loader" aria-hidden="true" />
      <CircleAlert v-else-if="state === 'error'" :size="20" aria-hidden="true" />
      <Database v-else :size="20" aria-hidden="true" />
      <span class="status-copy">
        <strong>{{ state === 'loading' ? '正在加载地图' : state === 'error' ? '地图暂时无法加载' : '暂无地图数据' }}</strong>
        <small>{{ message }}</small>
      </span>
      <button v-if="state === 'error'" type="button" @click="$emit('retry')">重试</button>
    </div>
  </div>
</template>

<style scoped>
.status-overlay { position: absolute; z-index: 15; inset: 0; display: grid; place-items: center; padding: 24px; background: rgb(243 241 236 / 62%); }
.status-card { display: grid; width: min(340px, 100%); grid-template-columns: 22px minmax(0, 1fr) auto; align-items: center; gap: 10px; border: 1px solid var(--ui-border); border-radius: var(--ui-radius); background: var(--ui-surface); padding: 12px 12px 12px 14px; box-shadow: var(--ui-shadow); color: var(--ui-primary); }
.loader { width: 19px; height: 19px; border: 2px solid #d8e0e5; border-top-color: var(--ui-accent); border-radius: 50%; animation: spin .8s linear infinite; }
.status-copy { display: grid; min-width: 0; gap: 2px; }
strong { color: var(--ui-text); font-size: 13px; }
small { overflow: hidden; color: var(--ui-text-secondary); font-size: 10px; line-height: 1.35; text-overflow: ellipsis; white-space: nowrap; }
button { min-height: 34px; border: 0; border-radius: 9px; background: var(--ui-primary); padding: 0 12px; color: white; font-size: 12px; font-weight: 700; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
