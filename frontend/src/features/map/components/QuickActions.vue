<script setup lang="ts">
import { BedDouble, ClipboardCheck, Ellipsis, School, Utensils } from '@lucide/vue'

const actions = [
  { label: '报到', icon: ClipboardCheck },
  { label: '教学楼', icon: School },
  { label: '食堂', icon: Utensils },
  { label: '宿舍', icon: BedDouble },
  { label: '更多', icon: Ellipsis },
]

defineEmits<{ choose: [label: string] }>()
</script>

<template>
  <div class="quick-list" aria-label="快捷分类入口">
    <button v-for="action in actions" :key="action.label" type="button" @click="$emit('choose', action.label)">
      <component :is="action.icon" :size="19" :stroke-width="1.8" aria-hidden="true" />
      <span>{{ action.label }}</span>
    </button>
  </div>
</template>

<style scoped>
.quick-list { display: grid; width: min(420px, calc(100vw - 24px)); grid-template-columns: repeat(5, minmax(0, 1fr)); overflow: hidden; border: 1px solid var(--ui-border); border-radius: var(--ui-radius); background: var(--ui-surface); padding: 5px 4px max(5px, env(safe-area-inset-bottom)); box-shadow: var(--ui-shadow-raised); }
button { display: grid; min-width: 0; min-height: 52px; place-items: center; align-content: center; gap: 3px; border: 0; background: transparent; color: var(--ui-text-secondary); font-size: 10px; font-weight: 650; transition: background var(--ui-motion), color var(--ui-motion); }
button:hover { background: var(--ui-surface-muted); color: var(--ui-primary); }
button:active { color: var(--ui-accent); }
button span { overflow: hidden; max-width: 100%; text-overflow: ellipsis; white-space: nowrap; }
</style>
