import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/api/client'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
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

    // Public landing + hosts + auth pages
    {
      path: '/',
      component: () => import('@/components/layout/PublicLayout.vue'),
      meta: { public: true },
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/public/HomeView.vue'),
        },
        {
          path: 'hosts',
          name: 'hosts',
          component: () => import('@/views/public/HostsView.vue'),
        },
        {
          path: 'login',
          name: 'login',
          component: () => import('@/views/auth/LoginView.vue'),
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('@/views/auth/RegisterView.vue'),
        },
      ],
    },

    // Public booking routes
    {
      path: '/book',
      component: () => import('@/components/layout/PublicLayout.vue'),
      meta: { public: true },
      children: [
        {
          path: ':slug',
          name: 'public-profile',
          component: () => import('@/views/public/PublicProfileView.vue'),
        },
        {
          path: ':slug/schedules/:scheduleId/slots',
          name: 'public-slots',
          component: () => import('@/views/public/SlotPickerView.vue'),
        },
        {
          path: ':slug/schedules/:scheduleId/book',
          name: 'public-booking-form',
          component: () => import('@/views/public/BookingFormView.vue'),
        },
        {
          path: ':slug/schedules/:scheduleId/done',
          name: 'public-booking-confirm',
          component: () => import('@/views/public/BookingConfirmView.vue'),
        },
      ],
    },

    // Token-based guest confirm (via link)
    {
      path: '/bookings/confirm/:token',
      name: 'booking-confirm-token',
      component: () => import('@/views/public/BookingConfirmView.vue'),
      meta: { public: true },
      props: (route) => ({ confirmToken: route.params.token }),
    },

    // Token-based guest cancel (via link)
    {
      path: '/bookings/cancel/:token',
      name: 'booking-cancel-token',
      component: () => import('@/views/public/BookingConfirmView.vue'),
      meta: { public: true },
      props: (route) => ({ cancelToken: route.params.token }),
    },

    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to) => {
  const isPublic = to.meta.public === true
  const hasToken = !!getToken()

  if (!isPublic && !hasToken) {
    return { name: 'login' }
  }

  if (isPublic && hasToken && (to.name === 'login' || to.name === 'register' || to.name === 'home')) {
    return { path: '/dashboard' }
  }
})

export default router
