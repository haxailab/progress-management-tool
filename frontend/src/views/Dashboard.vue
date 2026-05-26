<template>
  <div class="p-8">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">ダッシュボード</h1>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600">読み込み中...</p>
    </div>

    <div v-else-if="stats">
      <!-- 統計カード -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-primary-100 text-primary-600">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-500 text-sm">プロジェクト</p>
              <p class="text-3xl font-bold text-gray-800">{{ stats.total_projects }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-blue-100 text-blue-600">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-500 text-sm">全課題</p>
              <p class="text-3xl font-bold text-gray-800">{{ stats.total_issues }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-yellow-100 text-yellow-600">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-500 text-sm">担当課題</p>
              <p class="text-3xl font-bold text-gray-800">{{ stats.my_assigned_issues }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="p-3 rounded-full bg-red-100 text-red-600">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-gray-500 text-sm">期限切れ</p>
              <p class="text-3xl font-bold text-gray-800">{{ stats.overdue_issues }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 参加申請通知 -->
      <div v-if="pendingRequests.length > 0" class="bg-yellow-50 border border-yellow-200 rounded-lg shadow mb-8">
        <div class="px-6 py-4 border-b border-yellow-200 bg-yellow-100">
          <div class="flex items-center">
            <svg class="w-6 h-6 text-yellow-600 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
            </svg>
            <h2 class="text-xl font-bold text-yellow-800">プロジェクト参加申請 ({{ pendingRequests.length }}件)</h2>
          </div>
        </div>
        <div class="divide-y divide-yellow-200">
          <div
            v-for="request in pendingRequests"
            :key="request.id"
            class="p-4 hover:bg-yellow-100 cursor-pointer transition"
            @click="goToProjectMembers(request.project_id)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <h3 class="font-medium text-gray-900">
                  {{ request.project?.name }} ({{ request.project?.key }})
                </h3>
                <div class="mt-1 text-sm text-gray-600">
                  <span class="font-medium">{{ request.user?.username }}</span> さんからの参加申請
                </div>
                <div v-if="request.message" class="mt-2 text-sm text-gray-600 bg-white p-2 rounded">
                  {{ request.message }}
                </div>
              </div>
              <div class="ml-4">
                <button class="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700">
                  確認する
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近の課題 -->
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">最近の課題</h2>
        </div>

        <div v-if="stats.recent_issues.length === 0" class="p-6 text-center text-gray-500">
          課題がありません
        </div>

        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="issue in stats.recent_issues"
            :key="issue.id"
            class="p-4 hover:bg-gray-50 cursor-pointer transition"
            @click="goToIssue(issue.id)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <h3 class="font-medium text-gray-900">{{ issue.title }}</h3>
                <div class="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                  <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                    :class="getStatusClass(issue.status)">
                    {{ issue.status }}
                  </span>
                  <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                    :class="getPriorityClass(issue.priority)">
                    {{ issue.priority }}
                  </span>
                  <span v-if="issue.assignee">
                    担当: {{ issue.assignee.username }}
                  </span>
                </div>
              </div>
              <div class="ml-4 text-sm text-gray-500">
                {{ formatDate(issue.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import axios from 'axios'
import { format } from 'date-fns'

const router = useRouter()
const stats = ref(null)
const loading = ref(true)
const pendingRequests = ref([])

onMounted(async () => {
  try {
    const response = await api.dashboard.get()
    stats.value = response.data

    // 参加申請を取得
    await fetchPendingRequests()
  } catch (error) {
    console.error('Failed to fetch dashboard:', error)
  } finally {
    loading.value = false
  }
})

async function fetchPendingRequests() {
  try {
    // 自分が参加しているプロジェクトの参加申請を取得
    const projectsResponse = await api.projects.list()
    const projects = projectsResponse.data

    const allRequests = []
    for (const project of projects) {
      try {
        const requestsResponse = await axios.get(`/api/projects/${project.id}/join-requests`)
        const requests = requestsResponse.data.map(req => ({
          ...req,
          project_id: project.id,
          project: project
        }))
        allRequests.push(...requests)
      } catch (error) {
        // プロジェクトにアクセス権がない場合は無視
      }
    }

    pendingRequests.value = allRequests
  } catch (error) {
    console.error('Failed to fetch pending requests:', error)
  }
}

const goToIssue = (id) => {
  router.push(`/issues/${id}`)
}

const goToProjectMembers = (projectId) => {
  router.push(`/projects/${projectId}/members`)
}

const formatDate = (dateString) => {
  return format(new Date(dateString), 'yyyy/MM/dd HH:mm')
}

const getStatusClass = (status) => {
  const classes = {
    '未対応': 'bg-gray-100 text-gray-800',
    '処理中': 'bg-blue-100 text-blue-800',
    'レビュー': 'bg-yellow-100 text-yellow-800',
    '完了': 'bg-green-100 text-green-800',
    '終了': 'bg-gray-100 text-gray-600'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getPriorityClass = (priority) => {
  const classes = {
    '低': 'bg-blue-100 text-blue-800',
    '中': 'bg-yellow-100 text-yellow-800',
    '高': 'bg-orange-100 text-orange-800',
    '最重要': 'bg-red-100 text-red-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}
</script>
