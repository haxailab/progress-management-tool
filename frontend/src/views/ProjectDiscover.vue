<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">プロジェクトを探す</h1>
      <router-link
        to="/my-join-requests"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        申請状況を確認
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-8">
      読み込み中...
    </div>

    <div v-else-if="projects.length === 0" class="text-center py-8 text-gray-500">
      プロジェクトがありません
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="project in projects"
        :key="project.id"
        class="bg-white rounded-lg shadow p-6 relative"
      >
        <!-- ステータスバッジ -->
        <div class="absolute top-4 right-4">
          <span
            v-if="project.membership_status === 'joined'"
            class="px-3 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800"
          >
            参加済み
          </span>
          <span
            v-else-if="project.membership_status === 'pending'"
            class="px-3 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800"
          >
            申請中
          </span>
          <span
            v-else
            class="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800"
          >
            参加可能
          </span>
        </div>

        <div class="flex items-start justify-between mb-4 pr-20">
          <div>
            <h3 class="text-lg font-semibold">{{ project.name }}</h3>
            <span class="text-sm text-gray-500">{{ project.key }}</span>
          </div>
        </div>

        <p class="text-gray-600 mb-4 line-clamp-3">
          {{ project.description || '説明なし' }}
        </p>

        <!-- ボタン -->
        <button
          v-if="project.membership_status === 'joined'"
          @click="goToProject(project.id)"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          プロジェクトを開く
        </button>
        <button
          v-else-if="project.membership_status === 'pending'"
          disabled
          class="w-full px-4 py-2 bg-gray-300 text-gray-600 rounded-md cursor-not-allowed"
        >
          申請中
        </button>
        <button
          v-else
          @click="openJoinDialog(project)"
          class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
        >
          参加申請
        </button>
      </div>
    </div>

    <!-- 参加申請ダイアログ -->
    <div v-if="showJoinDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeJoinDialog">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mb-4">
          <h3 class="text-lg font-medium">プロジェクト参加申請</h3>
          <p class="text-sm text-gray-600 mt-2">{{ selectedProject?.name }} への参加を申請します</p>
        </div>

        <form @submit.prevent="submitJoinRequest">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">申請メッセージ（任意）</label>
            <textarea
              v-model="joinMessage"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              rows="4"
              placeholder="自己紹介や参加したい理由などを入力してください"
            ></textarea>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeJoinDialog"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              キャンセル
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              申請する
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
import axios from 'axios'

const router = useRouter()
const projects = ref([])
const loading = ref(true)
const showJoinDialog = ref(false)
const selectedProject = ref(null)
const joinMessage = ref('')

onMounted(() => {
  loadProjects()
})

async function loadProjects() {
  try {
    loading.value = true
    const response = await axios.get('/api/projects/all')
    projects.value = response.data
  } catch (error) {
    console.error('プロジェクト一覧の取得に失敗しました:', error)
    alert('プロジェクト一覧の取得に失敗しました')
  } finally {
    loading.value = false
  }
}

function goToProject(projectId) {
  router.push(`/projects/${projectId}`)
}

function openJoinDialog(project) {
  selectedProject.value = project
  joinMessage.value = ''
  showJoinDialog.value = true
}

function closeJoinDialog() {
  showJoinDialog.value = false
  selectedProject.value = null
  joinMessage.value = ''
}

async function submitJoinRequest() {
  try {
    await axios.post(`/api/projects/${selectedProject.value.id}/join-requests`, {
      project_id: selectedProject.value.id,
      message: joinMessage.value || null
    })
    closeJoinDialog()
    alert('参加申請を送信しました')
    await loadProjects()
  } catch (error) {
    console.error('参加申請に失敗しました:', error)
    alert(error.response?.data?.detail || '参加申請に失敗しました')
  }
}
</script>
