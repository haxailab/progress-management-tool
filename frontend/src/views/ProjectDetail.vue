<template>
  <div class="p-8">
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="project">
      <!-- ヘッダー -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <div class="flex items-center space-x-3">
              <span class="px-3 py-1 bg-primary-100 text-primary-800 text-sm font-medium rounded">
                {{ project.key }}
              </span>
              <h1 class="text-3xl font-bold text-gray-800">{{ project.name }}</h1>
            </div>
            <p class="text-gray-600 mt-2">{{ project.description }}</p>
          </div>
        </div>

        <!-- ナビゲーション -->
        <div class="border-b border-gray-200">
          <nav class="flex space-x-8">
            <button
              @click="currentTab = 'issues'"
              class="py-4 px-1 border-b-2 font-medium text-sm"
              :class="currentTab === 'issues' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            >
              課題
            </button>
            <button
              @click="goToGantt"
              class="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
            >
              ガントチャート
            </button>
            <button
              @click="goToWiki"
              class="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
            >
              Wiki
            </button>
            <button
              @click="goToFiles"
              class="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300"
            >
              ファイル
            </button>
            <button
              @click="goToMembers"
              class="py-4 px-1 border-b-2 border-transparent font-medium text-sm text-gray-500 hover:text-gray-700 hover:border-gray-300 relative"
            >
              メンバー
              <span v-if="pendingRequestsCount > 0" class="absolute -top-1 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {{ pendingRequestsCount }}
              </span>
            </button>
          </nav>
        </div>
      </div>

      <!-- 課題タブ -->
      <div v-if="currentTab === 'issues'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-800">課題一覧</h2>
          <button
            @click="showCreateIssue = true"
            class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            新規課題
          </button>
        </div>

        <div v-if="issuesLoading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>

        <div v-else-if="issues.length === 0" class="text-center py-8 text-gray-500">
          課題がありません
        </div>

        <div v-else class="bg-white rounded-lg shadow overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">課題</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ステータス</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">優先度</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">担当者</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">期限</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="issue in issues"
                :key="issue.id"
                class="hover:bg-gray-50 cursor-pointer"
                @click="goToIssue(issue.id)"
              >
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-gray-900">
                    {{ project.key }}-{{ issue.issue_number }}
                  </div>
                  <div class="text-sm text-gray-500">{{ issue.title }}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="getStatusClass(issue.status)">
                    {{ issue.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                    :class="getPriorityClass(issue.priority)">
                    {{ issue.priority }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ issue.assignee?.username || '未割り当て' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ issue.due_date || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 課題作成モーダル -->
    <div v-if="showCreateIssue" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-screen overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">新規課題</h2>
        </div>

        <form @submit.prevent="createIssue" class="p-6">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">
              タイトル *
            </label>
            <input
              v-model="newIssue.title"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">
              説明
            </label>
            <textarea
              v-model="newIssue.description"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">
                ステータス
              </label>
              <select
                v-model="newIssue.status"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="未対応">未対応</option>
                <option value="処理中">処理中</option>
                <option value="レビュー">レビュー</option>
                <option value="完了">完了</option>
                <option value="終了">終了</option>
              </select>
            </div>

            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">
                優先度
              </label>
              <select
                v-model="newIssue.priority"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="低">低</option>
                <option value="中">中</option>
                <option value="高">高</option>
                <option value="最重要">最重要</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">
                担当者
              </label>
              <select
                v-model="newIssue.assignee_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option :value="null">未割り当て</option>
                <option v-for="user in users" :key="user.id" :value="user.id">
                  {{ user.username }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">
                開始日
              </label>
              <input
                v-model="newIssue.start_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">
                期限
              </label>
              <input
                v-model="newIssue.due_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div v-if="createError" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
            {{ createError }}
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showCreateIssue = false"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              type="submit"
              :disabled="creating"
              class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50"
            >
              {{ creating ? '作成中...' : '作成' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const issues = ref([])
const users = ref([])
const loading = ref(true)
const pendingRequestsCount = ref(0)
const issuesLoading = ref(true)
const currentTab = ref('issues')
const showCreateIssue = ref(false)
const creating = ref(false)
const createError = ref('')

const newIssue = ref({
  title: '',
  description: '',
  status: '未対応',
  priority: '中',
  assignee_id: null,
  start_date: null,
  due_date: null
})

const projectId = computed(() => parseInt(route.params.id))

onMounted(async () => {
  await Promise.all([
    fetchProject(),
    fetchIssues(),
    fetchPendingRequestsCount(),
    fetchUsers()
  ])
})

const fetchProject = async () => {
  try {
    const response = await api.projects.get(projectId.value)
    project.value = response.data
  } catch (err) {
    console.error('Failed to fetch project:', err)
  } finally {
    loading.value = false
  }
}

const fetchIssues = async () => {
  try {
    const response = await api.issues.list(projectId.value)
    issues.value = response.data
  } catch (err) {
    console.error('Failed to fetch issues:', err)
  } finally {
    issuesLoading.value = false
  }
}

const fetchUsers = async () => {
  try {
    const response = await api.users.list()
    users.value = response.data
  } catch (err) {
    console.error('Failed to fetch users:', err)
  }
}

const createIssue = async () => {
  creating.value = true
  createError.value = ''

  try {
    await api.issues.create({
      ...newIssue.value,
      project_id: projectId.value
    })
    showCreateIssue.value = false
    newIssue.value = {
      title: '',
      description: '',
      status: '未対応',
      priority: '中',
      assignee_id: null,
      start_date: null,
      due_date: null
    }
    await fetchIssues()
  } catch (err) {
    createError.value = err.response?.data?.detail || '課題の作成に失敗しました'
  } finally {
    creating.value = false
  }
}

const goToIssue = (id) => {
  router.push(`/issues/${id}`)
}

const goToGantt = () => {
  router.push(`/projects/${projectId.value}/gantt`)
}

const goToWiki = () => {
  router.push(`/projects/${projectId.value}/wiki`)
}

const goToFiles = () => {
  router.push(`/projects/${projectId.value}/files`)
}

const goToMembers = () => {
  router.push(`/projects/${projectId.value}/members`)
}

async function fetchPendingRequestsCount() {
  try {
    const response = await api.get(`/api/projects/${projectId.value}/join-requests`)
    pendingRequestsCount.value = response.data.length
  } catch (error) {
    // メンバーでない場合はエラーになるが、無視する
    pendingRequestsCount.value = 0
  }
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
