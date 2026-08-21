import { createRouter, createWebHistory } from 'vue-router'

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'campus-map',
      component: () => import('@/features/map/components/CampusMap.vue'),
    },
  ],
})
