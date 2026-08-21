<script setup lang="ts">
defineProps<{ locating: boolean; disabled: boolean }>()
defineEmits<{ locate: []; reset: [] }>()
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
      <svg v-else aria-hidden="true" viewBox="0 0 24 24"><path d="M12 3v3m0 12v3M3 12h3m12 0h3m-4 0a5 5 0 1 1-10 0 5 5 0 0 1 10 0Z" /></svg>
    </button>
    <button
      type="button"
      :disabled="disabled"
      title="返回校园默认视角"
      aria-label="返回校园默认视角"
      @click="$emit('reset')"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m4 11 8-7 8 7v8a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8Z" /></svg>
    </button>
  </div>
</template>

<style scoped>
.control-stack { display: grid; gap: 8px; }
button { display: grid; width: 46px; height: 46px; place-items: center; border: 1px solid rgb(255 255 255 / 80%); border-radius: 15px; background: rgb(255 255 255 / 92%); box-shadow: 0 8px 24px rgb(25 54 43 / 15%); color: #294b3f; backdrop-filter: blur(12px); }
button:hover:not(:disabled) { background: #fff; color: #075ea8; }
button:disabled { cursor: wait; opacity: .55; }
button:focus-visible { outline: 3px solid rgb(7 94 168 / 30%); outline-offset: 2px; }
svg { width: 22px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.9; }
.spinner { width: 19px; height: 19px; border: 2px solid #b9c9c1; border-top-color: #075ea8; border-radius: 50%; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
