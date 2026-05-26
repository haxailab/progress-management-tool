<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-6">プロジェクトメンバー</h2>

    <!-- 参加申請一覧 -->
    <div v-if="joinRequests.length > 0" class="mb-8">
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4 rounded">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-yellow-600 mr-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z"/>
          </svg>
          <div>
            <h3 class="text-lg font-semibold text-yellow-800">参加申請待ち ({{ joinRequests.length }}件)</h3>
            <p class="text-sm text-yellow-700 mt-1">以下のユーザーがプロジェクトへの参加を希望しています</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ユーザー
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                メッセージ
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                申請日
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in joinRequests" :key="request.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ request.user?.username }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ request.user?.email }}
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900 max-w-md">
                  {{ request.message || '-' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(request.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex items-center space-x-4">
                  <button
                    @click="approveRequest(request.id)"
                    class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium shadow-sm transition"
                  >
                    ✓ 承認
                  </button>
                  <button
                    @click="rejectRequest(request.id)"
                    class="px-4 py-2 bg-white text-red-600 border-2 border-red-600 rounded-md hover:bg-red-50 font-medium transition"
                  >
                    × 却下
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- メンバー一覧 -->
    <div>
      <h3 class="text-lg font-semibold mb-4">メンバー一覧</h3>
      <div v-if="membersLoading" class="text-center py-8">
        読み込み中...
      </div>

      <div v-else-if="members.length === 0" class="text-center py-8 text-gray-500">
        メンバーがいません
      </div>

      <div v-else class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ユーザー名
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                メールアドレス
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                氏名
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                役割
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                参加日
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="member in members" :key="member.id">
              <td class="px-6 py-4 whitespace-nowrap">
                {{ member.user?.username }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ member.user?.email }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ member.user?.full_name || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  member.role === 'owner' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                ]">
                  {{ member.role === 'owner' ? 'オーナー' : 'メンバー' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(member.joined_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  v-if="member.role !== 'owner'"
                  @click="removeMember(member.user_id)"
                  class="text-red-600 hover:text-red-900"
                >
                  削除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const projectId = ref(parseInt(route.params.id))

const members = ref([])
const membersLoading = ref(true)
const joinRequests = ref([])

onMounted(() => {
  loadMembers()
  loadJoinRequests()
})

async function loadMembers() {
  try {
    membersLoading.value = true
    const response = await axios.get(`/api/projects/${projectId.value}/members`)
    members.value = response.data
  } catch (error) {
    console.error('メンバー一覧の取得に失敗しました:', error)
    alert('メンバー一覧の取得に失敗しました')
  } finally {
    membersLoading.value = false
  }
}

async function loadJoinRequests() {
  try {
    const response = await axios.get(`/api/projects/${projectId.value}/join-requests`)
    joinRequests.value = response.data
  } catch (error) {
    console.error('参加申請一覧の取得に失敗しました:', error)
  }
}

async function approveRequest(requestId) {
  const request = joinRequests.value.find(r => r.id === requestId)
  const userName = request?.user?.username || 'このユーザー'

  if (!confirm(`${userName} さんの参加申請を承認してもよろしいですか？\n\n承認すると、このプロジェクトのメンバーとして追加されます。`)) {
    return
  }

  try {
    await axios.post(`/api/join-requests/${requestId}/approve`)
    alert('✓ 参加申請を承認しました')
    await loadJoinRequests()
    await loadMembers()
  } catch (error) {
    console.error('承認に失敗しました:', error)
    alert(error.response?.data?.detail || '承認に失敗しました')
  }
}

async function rejectRequest(requestId) {
  const request = joinRequests.value.find(r => r.id === requestId)
  const userName = request?.user?.username || 'このユーザー'

  if (!confirm(`${userName} さんの参加申請を却下してもよろしいですか？\n\n⚠️ この操作は取り消せません。ユーザーは再度申請する必要があります。`)) {
    return
  }

  try {
    await axios.post(`/api/join-requests/${requestId}/reject`)
    alert('参加申請を却下しました')
    await loadJoinRequests()
  } catch (error) {
    console.error('却下に失敗しました:', error)
    alert(error.response?.data?.detail || '却下に失敗しました')
  }
}

async function removeMember(userId) {
  if (!confirm('このメンバーを削除してもよろしいですか？')) {
    return
  }

  try {
    await axios.delete(`/api/projects/${projectId.value}/members/${userId}`)
    alert('メンバーを削除しました')
    await loadMembers()
  } catch (error) {
    console.error('メンバー削除に失敗しました:', error)
    alert(error.response?.data?.detail || 'メンバー削除に失敗しました')
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('ja-JP')
}
</script>
