<script setup lang="ts">
import { Compass, LocateFixed, MapPinned } from '@lucide/vue'

defineProps<{ locating: boolean; disabled: boolean }>()
defineEmits<{ locate: []; compass: []; reset: [] }>()
</script>

<template>
  <div class="control-stack" aria-label="地图控制">
    <button
      type="button"
      :disabled="disabled || locating"
      :title="locating ? '正在定位' : '定位到我的位置'"
      aria-label="定位到我的位置"
      @click="$emit('locate')"
    >
      <span v-if="locating" class="spinner" aria-hidden="true" />
      <LocateFixed v-else :size="20" :stroke-width="1.9" aria-hidden="true" />
    </button>
    <button
      type="button"
      :disabled="disabled"
      title="指南针归北"
      aria-label="指南针归北"
      @click="$emit('compass')"
    >
      <Compass :size="20" :stroke-width="1.9" aria-hidden="true" />
    </button>
    <button
      type="button"
      :disabled="disabled"
      title="返回校园默认视角"
      aria-label="返回校园默认视角"
      @click="$emit('reset')"
    >
      <MapPinned :size="20" :stroke-width="1.9" aria-hidden="true" />
    </button>
  </div>
</template>

<style scoped>
.control-stack { display: grid; overflow: hidden; border: 1px solid var(--ui-border); border-radius: var(--ui-radius); background: var(--ui-surface); box-shadow: var(--ui-shadow); }
button { display: grid; width: 42px; height: 42px; place-items: center; border: 0; border-bottom: 1px solid var(--ui-border); background: transparent; color: var(--ui-primary); transition: background var(--ui-motion), color var(--ui-motion); }
button:last-child { border-bottom: 0; }
button:hover:not(:disabled) { background: var(--ui-surface-muted); color: var(--ui-accent); }
button:disabled { cursor: wait; opacity: .55; }
.spinner { width: 18px; height: 18px; border: 2px solid #cbd4db; border-top-color: var(--ui-accent); border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
