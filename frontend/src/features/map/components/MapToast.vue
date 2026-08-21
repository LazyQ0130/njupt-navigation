<script setup lang="ts">
import { X } from '@lucide/vue'

defineProps<{ message: string; actionLabel?: string; secondaryLabel?: string }>()
defineEmits<{ action: []; secondary: []; close: [] }>()
</script>

<template>
  <div v-if="message" class="toast" role="status" aria-live="polite">
    <p>{{ message }}</p>
    <div v-if="actionLabel || secondaryLabel" class="actions">
      <button v-if="actionLabel" type="button" @click="$emit('action')">{{ actionLabel }}</button>
      <button v-if="secondaryLabel" class="secondary" type="button" @click="$emit('secondary')">{{ secondaryLabel }}</button>
    </div>
    <button class="close" type="button" aria-label="关闭提示" @click="$emit('close')">
      <X :size="17" :stroke-width="2" aria-hidden="true" />
    </button>
  </div>
</template>

<style scoped>
.toast { position: relative; width: min(420px, calc(100vw - 24px)); border: 1px solid rgb(255 255 255 / 12%); border-radius: 10px; background: #17242e; padding: 10px 38px 10px 13px; box-shadow: 0 5px 16px rgb(20 33 43 / 22%); color: white; animation: toast-in 180ms ease-out; }
p { margin: 0; font-size: 12px; line-height: 1.45; }
.actions { display: flex; gap: 8px; margin-top: 10px; }
.actions button { border: 0; border-radius: 7px; background: #eaf2ff; padding: 6px 9px; color: var(--ui-primary); font-size: 11px; font-weight: 750; }
.actions .secondary { background: rgb(255 255 255 / 11%); color: #fff; }
.close { position: absolute; top: 4px; right: 5px; display: grid; width: 30px; height: 30px; place-items: center; border: 0; border-radius: 8px; background: transparent; color: #cbd5dc; }
.close:hover { background: rgb(255 255 255 / 8%); color: white; }
@keyframes toast-in { from { opacity: 0; transform: translateY(6px); } }
</style>
