const MonitoringVsosh = () => import('@/pages/MonitoringVsoshPage.vue')

const monitoringRoutes = [
  {
    path: '/',
    name: 'Monitoring',
    component: MonitoringVsosh,
    meta: {
      title: 'Главная',
      requiresAuth: true,
    },
  },
]

export default monitoringRoutes
