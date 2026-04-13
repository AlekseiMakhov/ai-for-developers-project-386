import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/api/client'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Auth
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { public: true },
    },

    // Dashboard
    {
      path: '/dashboard',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/dashboard/SchedulesView.vue'),
        },
        {
          path: '/bookings',
          name: 'bookings',
          component: () => import('@/views/dashboard/BookingsView.vue'),
        },
      ],
    },

    // Public booking routes — added in iteration 3
    { path: '/', redirect: '/dashboard' },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
})

router.beforeEach((to) => {
  const isPublic = to.meta.public === true
  const hasToken = !!getToken()

  if (!isPublic && !hasToken) {
    return { name: 'login' }
  }

  if (isPublic && hasToken && (to.name === 'login' || to.name === 'register')) {
    return { path: '/dashboard' }
  }
})

export default router
