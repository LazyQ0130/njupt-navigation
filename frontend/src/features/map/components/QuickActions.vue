<script setup lang="ts">
const actions = [
  { label: '教学楼', icon: '教' },
  { label: '食堂', icon: '餐' },
  { label: '宿舍', icon: '住' },
  { label: '运动', icon: '动' },
]

defineEmits<{ choose: [label: string] }>()
</script>

<template>
  <div class="quick-list" aria-label="快捷分类入口">
    <button v-for="action in actions" :key="action.label" type="button" @click="$emit('choose', action.label)">
      <span aria-hidden="true">{{ action.icon }}</span>{{ action.label }}
    </button>
  </div>
</template>

<style scoped>
.quick-list { display: flex; max-width: calc(100vw - 32px); gap: 8px; overflow-x: auto; padding: 2px; scrollbar-width: none; }
.quick-list::-webkit-scrollbar { display: none; }
button { display: flex; min-height: 38px; flex: 0 0 auto; align-items: center; gap: 7px; border: 1px solid rgb(255 255 255 / 80%); border-radius: 999px; background: rgb(255 255 255 / 88%); padding: 5px 12px 5px 7px; box-shadow: 0 7px 18px rgb(30 58 45 / 11%); color: #344c42; font-size: 12px; font-weight: 650; backdrop-filter: blur(12px); }
button span { display: grid; width: 27px; height: 27px; place-items: center; border-radius: 50%; background: #e4efe7; color: #245a46; font-size: 11px; }
button:focus-visible { outline: 3px solid rgb(7 94 168 / 30%); outline-offset: 2px; }
</style>
