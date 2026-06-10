const Login = () => import('@/pages/LoginPage.vue')
const Profile = () => import('@/pages/ProfilePage.vue')

const authRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: 'Авторизация',
      requiresGuest: true,
    },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: {
      title: 'Профиль',
      requiresAuth: true,
    },
  },
]

export default authRoutes
