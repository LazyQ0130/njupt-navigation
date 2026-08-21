<script setup lang="ts">
import { Search } from '@lucide/vue'

defineEmits<{ activate: [] }>()
</script>

<template>
  <button class="search-shell" type="button" aria-label="搜索地点，Phase 2 开放" @click="$emit('activate')">
    <span class="brand-cue" aria-hidden="true">南邮</span>
    <Search :size="20" :stroke-width="2" aria-hidden="true" />
    <span class="placeholder">搜索教学楼、食堂、宿舍…</span>
  </button>
</template>

<style scoped>
.search-shell {
  display: flex;
  width: min(560px, calc(100vw - 32px));
  height: 50px;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  border: 1px solid var(--ui-border);
  border-radius: var(--ui-radius);
  background: var(--ui-surface);
  box-shadow: var(--ui-shadow);
  color: var(--ui-text-secondary);
  text-align: left;
  transition: box-shadow var(--ui-motion), transform var(--ui-motion);
}
.search-shell:hover { box-shadow: var(--ui-shadow-raised); }
.search-shell:active { transform: translateY(1px); }
.brand-cue { flex: 0 0 auto; border-right: 1px solid var(--ui-border); padding-right: 10px; color: var(--ui-primary); font-size: 12px; font-weight: 800; letter-spacing: .04em; }
svg { flex: 0 0 auto; color: var(--ui-primary); }
.placeholder { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px; }
</style>
