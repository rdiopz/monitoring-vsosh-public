import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@entities/auth'

import authRoutes from './modules/auth'
import monitoringRoutes from './modules/vsosh'

const NotFound = () => import('@/pages/NotFoundPage.vue')

const baseRoutes = [
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: 'Страница не найдена',
    },
  },
]

const routes = [...monitoringRoutes, ...authRoutes, ...baseRoutes.slice(-1)]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // Поведение прокрутки при переходе между маршрутами
  scrollBehavior(to, from, savedPosition) {
    if (to.path === from.path) {
      return false
    }

    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
        top: 50,
      }
    } else {
      return { top: 0 }
    }
  },
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Пытаемся проверить имеется ли refresh token в cookie через запрос к api
  if (!authStore.isInitialized) {
    await authStore.initializeAuth()
  }

  // Простая логика: если не на логине и не авторизован - на логин
  if (to.name !== 'Login' && !authStore.isAuthenticated) {
    return next({ name: 'Login' })
  }

  // Если на логине и авторизован - на мониторинг
  if (to.name === 'Login' && authStore.isAuthenticated) {
    return next({ name: 'Monitoring' })
  }

  next()
})

export default router
