<script setup lang="ts">
import type { ReviewLayerGroup, SelectedReview } from '../types'

defineProps<{
  visibility: Record<ReviewLayerGroup, boolean>
  selected?: SelectedReview
}>()

const emit = defineEmits<{
  toggle: [group: ReviewLayerGroup, visible: boolean]
}>()

const groups: Array<{ key: ReviewLayerGroup, label: string }> = [
  { key: 'buildings', label: 'Buildings' },
  { key: 'roads', label: 'Roads' },
  { key: 'pois', label: 'POIs' },
  { key: 'endpoints', label: 'Disconnected Endpoints' },
  { key: 'intersections', label: 'Intersection Warnings' },
  { key: 'candidates', label: 'Candidate Entrances' },
  { key: 'verification', label: 'Verification Status' },
]
</script>

<template>
  <section class="review-panel" aria-label="GIS review mode">
    <header>
      <strong>GIS Review · DEV ONLY</strong>
      <span><b class="p0" /> P0 <b class="p1" /> P1 <b class="p2" /> P2</span>
    </header>
    <label v-for="group in groups" :key="group.key">
      <input
        type="checkbox"
        :checked="visibility[group.key]"
        @change="emit('toggle', group.key, ($event.target as HTMLInputElement).checked)"
      >
      {{ group.label }}
    </label>
    <dl v-if="selected" class="selection">
      <dt>ID</dt><dd>{{ selected.id }}</dd>
      <dt>Name</dt><dd>{{ selected.name }}</dd>
      <dt>Source</dt><dd>{{ selected.source }}</dd>
      <dt>Verification</dt><dd>{{ selected.verification }}</dd>
      <dt>Severity</dt><dd>{{ selected.severity }}</dd>
      <dt>Warning</dt><dd>{{ selected.warning }}</dd>
    </dl>
    <p v-else>点击彩色审核对象查看来源与 warning。</p>
  </section>
</template>

<style scoped>
.review-panel { width: min(340px, calc(100vw - 24px)); max-height: min(70vh, 620px); overflow: auto; padding: 12px; border: 1px solid #334155; border-radius: 10px; color: #e2e8f0; background: rgb(15 23 42 / 94%); box-shadow: 0 10px 30px rgb(0 0 0 / 24%); font: 12px/1.4 ui-monospace, SFMono-Regular, Consolas, monospace; }
header { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
header span { color: #cbd5e1; white-space: nowrap; }
header b { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.p0 { background: #ef4444; } .p1 { background: #f97316; } .p2 { background: #facc15; }
label { display: flex; align-items: center; gap: 7px; padding: 3px 0; }
.selection { display: grid; grid-template-columns: 86px 1fr; gap: 3px 8px; margin: 10px 0 0; padding-top: 8px; border-top: 1px solid #475569; }
dt { color: #94a3b8; } dd { min-width: 0; margin: 0; overflow-wrap: anywhere; }
p { margin: 9px 0 0; color: #94a3b8; }
</style>
