<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">参加申請状況</h1>
      <router-link
        to="/projects/discover"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        プロジェクトを探す
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-8">
      読み込み中...
    </div>

    <div v-else-if="requests.length === 0" class="text-center py-8 text-gray-500">
      参加申請はありません
    </div>

    <div v-else class="bg-white rounded-lg shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              プロジェクト
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              申請メッセージ
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ステータス
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              申請日
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              処理日
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="request in requests" :key="request.id">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">
                {{ request.project?.name }}
              </div>
              <div class="text-sm text-gray-500">
                {{ request.project?.key }}
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="text-sm text-gray-900 max-w-md truncate">
                {{ request.message || '-' }}
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                request.status === '申請中' ? 'bg-yellow-100 text-yellow-800' :
                request.status === '承認済み' ? 'bg-green-100 text-green-800' :
                'bg-red-100 text-red-800'
              ]">
                {{ request.status }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(request.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ request.reviewed_at ? formatDate(request.reviewed_at) : '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const requests = ref([])
const loading = ref(true)

onMounted(() => {
  loadRequests()
})

async function loadRequests() {
  try {
    loading.value = true
    const response = await axios.get('/api/my-join-requests')
    requests.value = response.data
  } catch (error) {
    console.error('参加申請一覧の取得に失敗しました:', error)
    alert('参加申請一覧の取得に失敗しました')
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('ja-JP')
}
</script>
