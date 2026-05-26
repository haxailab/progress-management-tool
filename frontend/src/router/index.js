import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue')
        },
        {
          path: '/projects',
          name: 'Projects',
          component: () => import('../views/Projects.vue')
        },
        {
          path: '/projects/:id',
          name: 'ProjectDetail',
          component: () => import('../views/ProjectDetail.vue')
        },
        {
          path: '/projects/:id/gantt',
          name: 'Gantt',
          component: () => import('../views/GanttSimple.vue')
        },
        {
          path: '/projects/:id/wiki',
          name: 'Wiki',
          component: () => import('../views/Wiki.vue')
        },
        {
          path: '/projects/:id/files',
          name: 'Files',
          component: () => import('../views/Files.vue')
        },
        {
          path: '/issues/:id',
          name: 'IssueDetail',
          component: () => import('../views/IssueDetail.vue')
        },
        {
          path: '/users',
          name: 'Users',
          component: () => import('../views/Users.vue')
        },
        {
          path: '/projects/discover',
          name: 'ProjectDiscover',
          component: () => import('../views/ProjectDiscover.vue')
        },
        {
          path: '/my-join-requests',
          name: 'MyJoinRequests',
          component: () => import('../views/MyJoinRequests.vue')
        },
        {
          path: '/projects/:id/members',
          name: 'ProjectMembers',
          component: () => import('../views/ProjectMembers.vue')
        },
        {
          path: '/multi-project-gantt',
          name: 'MultiProjectGantt',
          component: () => import('../views/MultiProjectGantt.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
