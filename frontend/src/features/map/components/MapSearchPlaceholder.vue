<script setup lang="ts">
defineEmits<{ activate: [] }>()
</script>

<template>
  <button class="search-shell" type="button" aria-label="搜索地点，Phase 2 开放" @click="$emit('activate')">
    <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m21 21-4.3-4.3m2.3-5.2a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0Z" /></svg>
    <span>搜索教学楼、食堂、服务点</span>
    <kbd>即将开放</kbd>
  </button>
</template>

<style scoped>
.search-shell {
  display: flex;
  width: min(560px, calc(100vw - 32px));
  min-height: 52px;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  border: 1px solid rgb(255 255 255 / 75%);
  border-radius: 18px;
  background: rgb(255 255 255 / 92%);
  box-shadow: 0 12px 32px rgb(30 58 45 / 16%);
  color: #667085;
  text-align: left;
  backdrop-filter: blur(14px);
}
.search-shell:focus-visible { outline: 3px solid rgb(7 94 168 / 30%); outline-offset: 3px; }
svg { width: 21px; fill: none; stroke: #214d3f; stroke-linecap: round; stroke-width: 2; }
span { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
kbd { border-radius: 999px; background: #edf5ef; padding: 5px 8px; color: #3f6b56; font: 600 10px/1 system-ui; }
@media (max-width: 480px) { kbd { display: none; } }
</style>
