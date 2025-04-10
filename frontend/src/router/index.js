import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../services/authService'
import Home from '../views/Home.vue'
import History from '../views/History.vue'
import About from '../views/About.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Profile from "../views/Profile.vue";

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: { requiresAuth: true }
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加全局导航守卫
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isGuestRoute = to.matched.some(record => record.meta.guest)

  // 如果需要身份验证且用户未登录，重定向到登录页面
  if (requiresAuth && !isAuthenticated()) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  }
  // 如果是访客路由(登录/注册)且用户已登录，重定向到首页
  else if (isGuestRoute && isAuthenticated()) {
    next({ path: '/' })
  }
  // 否则继续
  else {
    next()
  }
})

export default router