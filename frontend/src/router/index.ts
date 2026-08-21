import { createRouter, createWebHistory } from 'vue-router'
import PhaseZeroView from '@/views/PhaseZeroView.vue'

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'phase-zero',
      component: PhaseZeroView,
    },
  ],
})

