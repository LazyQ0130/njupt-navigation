<script setup lang="ts">
import { Building2, X } from '@lucide/vue'
import { computed } from 'vue'
import type { SelectedPlace } from '../types'

const props = defineProps<{ place: SelectedPlace }>()
defineEmits<{ close: [] }>()

const categoryLabel = computed(() => {
  if (props.place.category === 'DORMITORY' && props.place.dormitoryZone) {
    return `${props.place.dormitoryZone} · 学生宿舍`
  }
  return ({
  ADMINISTRATION: '行政服务',
  DINING: '餐饮服务',
  DORMITORY: '学生宿舍',
  LIBRARY: '图书馆',
  SERVICE: '校园服务',
  TEACHING: '教学建筑',
  }[props.place.category] ?? '校园建筑')
})

const secondaryName = computed(() => (
  props.place.officialName && props.place.officialName !== props.place.name
    ? props.place.officialName
    : undefined
))
</script>

<template>
  <section class="place-peek" role="status" aria-label="已选择地点">
    <span class="place-icon" aria-hidden="true">
      <Building2 :size="21" :stroke-width="1.8" />
    </span>
    <span class="place-copy">
      <small>{{ categoryLabel }}</small>
      <strong>{{ place.name }}</strong>
      <span v-if="secondaryName" class="official-name">{{ secondaryName }}</span>
    </span>
    <button type="button" aria-label="关闭地点信息" @click="$emit('close')">
      <X :size="18" :stroke-width="1.8" aria-hidden="true" />
    </button>
  </section>
</template>

<style scoped>
.place-peek { display: grid; grid-template-columns: 38px minmax(0, 1fr) 34px; align-items: center; gap: 10px; width: min(360px, calc(100vw - 24px)); border: 1px solid var(--ui-border); border-radius: var(--ui-radius); background: var(--ui-surface); padding: 10px 8px 10px 10px; box-shadow: var(--ui-shadow-raised); animation: place-in 200ms cubic-bezier(.2, .7, .2, 1); }
.place-icon { display: grid; width: 38px; height: 38px; place-items: center; border-radius: 10px; background: #edf3f8; color: var(--ui-primary); }
.place-copy { display: grid; min-width: 0; gap: 2px; }
small { color: var(--ui-text-secondary); font-size: 10px; font-weight: 650; }
strong { overflow: hidden; color: var(--ui-text); font-size: 14px; text-overflow: ellipsis; white-space: nowrap; }
.official-name { overflow: hidden; color: var(--ui-text-secondary); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
button { display: grid; width: 34px; height: 34px; place-items: center; border: 0; border-radius: 9px; background: transparent; color: var(--ui-text-secondary); }
button:hover { background: var(--ui-surface-muted); color: var(--ui-text); }
@keyframes place-in { from { opacity: 0; transform: translateY(10px); } }
@media (min-width: 768px) {
  .place-peek { width: 300px; }
}
</style>
