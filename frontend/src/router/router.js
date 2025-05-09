import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Auth from '../views/Auth.vue'
import Movies from '../views/Movies.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Auth',
    component: Auth
  },
  {
    path: '/movies',
    name: 'Movies',
    component: Movies,
    meta: { requiresAuth: true } // This route is for requiring authentication
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token')
    if (!token) {
      // Redirect to login if not authenticated
      next({ name: 'Auth' })
    } else {
      // Allow access if authenticated
      next()
    }
  } else {
    // No auth needed for this route
    next()
  }
})

export default router