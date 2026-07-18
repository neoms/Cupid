import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
  { path: '/create', name: 'CreateProfile', component: () => import('../views/CreateProfile.vue') },
  { path: '/search/natural', name: 'NaturalSearch', component: () => import('../views/NaturalSearch.vue') },
  { path: '/search/structured', name: 'StructuredSearch', component: () => import('../views/StructuredSearch.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
