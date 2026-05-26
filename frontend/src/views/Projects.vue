<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-800">プロジェクト</h1>
      <button
        @click="showCreateModal = true"
        class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        新規プロジェクト
      </button>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="projects.length === 0" class="text-center py-12 text-gray-500">
      プロジェクトがありません
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="project in projects"
        :key="project.id"
        class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer"
        @click="goToProject(project.id)"
      >
        <div class="p-6">
          <div class="flex items-center justify-between mb-4">
            <span class="px-3 py-1 bg-primary-100 text-primary-800 text-sm font-medium rounded">
              {{ project.key }}
            </span>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">{{ project.name }}</h3>
          <p class="text-gray-600 text-sm">{{ project.description || '説明なし' }}</p>
        </div>
      </div>
    </div>

    <!-- プロジェクト作成モーダル -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">新規プロジェクト</h2>
        </div>

        <form @submit.prevent="createProject" class="p-6">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">
              プロジェクト名
            </label>
            <input
              v-model="newProject.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">
              プロジェクトキー
            </label>
            <input
              v-model="newProject.key"
              type="text"
              required
              pattern="[A-Z0-9]+"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="例: PROJ"
            />
            <p class="text-xs text-gray-500 mt-1">半角大文字英数字のみ</p>
          </div>

          <div class="mb-6">
            <label class="block text-gray-700 text-sm font-bold mb-2">
              説明
            </label>
            <textarea
              v-model="newProject.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            ></textarea>
          </div>

          <div v-if="error" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
            {{ error }}
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showCreateModal = false"
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const projects = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const creating = ref(false)
const error = ref('')

const newProject = ref({
  name: '',
  key: '',
  description: ''
})

onMounted(async () => {
  await fetchProjects()
})

const fetchProjects = async () => {
  try {
    const response = await api.projects.list()
    projects.value = response.data
  } catch (err) {
    console.error('Failed to fetch projects:', err)
  } finally {
    loading.value = false
  }
}

const createProject = async () => {
  creating.value = true
  error.value = ''

  try {
    await api.projects.create(newProject.value)
    showCreateModal.value = false
    newProject.value = { name: '', key: '', description: '' }
    await fetchProjects()
  } catch (err) {
    error.value = err.response?.data?.detail || 'プロジェクトの作成に失敗しました'
  } finally {
    creating.value = false
  }
}

const goToProject = (id) => {
  router.push(`/projects/${id}`)
}
</script>
