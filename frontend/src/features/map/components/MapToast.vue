<script setup lang="ts">
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
    <button class="close" type="button" aria-label="关闭提示" @click="$emit('close')">×</button>
  </div>
</template>

<style scoped>
.toast { position: relative; width: min(520px, calc(100vw - 32px)); border: 1px solid rgb(255 255 255 / 30%); border-radius: 18px; background: rgb(26 48 40 / 94%); padding: 13px 42px 13px 16px; box-shadow: 0 15px 35px rgb(13 30 24 / 30%); color: white; backdrop-filter: blur(14px); }
p { margin: 0; font-size: 13px; line-height: 1.5; }
.actions { display: flex; gap: 8px; margin-top: 10px; }
.actions button { border: 0; border-radius: 9px; background: #f4b85a; padding: 7px 10px; color: #27372f; font-size: 12px; font-weight: 750; }
.actions .secondary { background: rgb(255 255 255 / 14%); color: #fff; }
.close { position: absolute; top: 8px; right: 9px; width: 30px; height: 30px; border: 0; background: transparent; color: #d6e1dc; font-size: 21px; }
</style>
