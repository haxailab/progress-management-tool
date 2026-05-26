<template>
  <div class="flex h-screen bg-gray-100">
    <!-- サイドバー -->
    <aside class="w-64 bg-primary-600 text-white shadow-lg">
      <div class="p-4 border-b border-primary-700">
        <h1 class="text-xl font-bold">プロジェクト管理</h1>
      </div>

      <nav class="p-4 space-y-2">
        <router-link
          to="/"
          class="flex items-center px-4 py-2 rounded hover:bg-primary-700 transition"
          :class="{ 'bg-primary-700': $route.name === 'Dashboard' }"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          ダッシュボード
        </router-link>

        <router-link
          to="/projects"
          class="flex items-center px-4 py-2 rounded hover:bg-primary-700 transition"
          :class="{ 'bg-primary-700': $route.name === 'Projects' }"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
          </svg>
          プロジェクト
        </router-link>

        <router-link
          to="/projects/discover"
          class="flex items-center px-4 py-2 rounded hover:bg-primary-700 transition"
          :class="{ 'bg-primary-700': $route.name === 'ProjectDiscover' }"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          プロジェクトを探す
        </router-link>

        <router-link
          to="/multi-project-gantt"
          class="flex items-center px-4 py-2 rounded hover:bg-primary-700 transition"
          :class="{ 'bg-primary-700': $route.name === 'MultiProjectGantt' }"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          進捗一覧管理
        </router-link>

        <router-link
          v-if="user?.is_admin"
          to="/users"
          class="flex items-center px-4 py-2 rounded hover:bg-primary-700 transition"
          :class="{ 'bg-primary-700': $route.name === 'Users' }"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          ユーザー管理
        </router-link>
      </nav>

      <div class="absolute bottom-0 w-64 p-4 border-t border-primary-700">
        <div class="flex items-center justify-between">
          <div v-if="user">
            <p class="text-sm font-medium">{{ user.username }}</p>
            <p class="text-xs text-primary-200">{{ user.email }}</p>
          </div>
          <button
            @click="handleLogout"
            class="p-2 rounded hover:bg-primary-700 transition"
            title="ログアウト"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- メインコンテンツ -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = computed(() => authStore.currentUser)

onMounted(() => {
  authStore.initAuth()
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
