<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">ユーザー管理</h1>
    </div>

    <div v-if="loading" class="text-center py-8">
      読み込み中...
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
              ステータス
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              権限
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              登録日
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="user in users" :key="user.id">
            <td class="px-6 py-4 whitespace-nowrap">
              {{ user.username }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              {{ user.email }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              {{ user.full_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              ]">
                {{ user.is_active ? '有効' : '無効' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                user.is_admin ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
              ]">
                {{ user.is_admin ? '管理者' : '一般' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ formatDate(user.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
              <button
                @click="openEditDialog(user)"
                class="text-indigo-600 hover:text-indigo-900"
              >
                編集
              </button>
              <button
                v-if="currentUser?.is_admin"
                @click="openResetPasswordDialog(user)"
                class="text-blue-600 hover:text-blue-900"
              >
                パスワードリセット
              </button>
              <button
                v-if="currentUser?.is_admin && user.id !== currentUser.id"
                @click="confirmDelete(user)"
                class="text-red-600 hover:text-red-900"
              >
                削除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 編集ダイアログ -->
    <div v-if="showEditDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeEditDialog">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mb-4">
          <h3 class="text-lg font-medium">ユーザー編集</h3>
        </div>

        <form @submit.prevent="saveUser">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">ユーザー名</label>
            <input
              v-model="editingUser.username"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">メールアドレス</label>
            <input
              v-model="editingUser.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">氏名</label>
            <input
              v-model="editingUser.full_name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div v-if="currentUser?.is_admin" class="mb-4">
            <label class="flex items-center">
              <input
                v-model="editingUser.is_active"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
              />
              <span class="ml-2 text-sm text-gray-700">アカウント有効</span>
            </label>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeEditDialog"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              キャンセル
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              保存
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- パスワードリセットダイアログ -->
    <div v-if="showResetPasswordDialog" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeResetPasswordDialog">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mb-4">
          <h3 class="text-lg font-medium">パスワードリセット</h3>
          <p class="text-sm text-gray-600 mt-2">{{ resetPasswordUser?.username }} のパスワードをリセットします</p>
        </div>

        <form @submit.prevent="resetPassword">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">新しいパスワード</label>
            <input
              v-model="newPassword"
              type="password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
              minlength="6"
            />
          </div>

          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">パスワード確認</label>
            <input
              v-model="confirmPassword"
              type="password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
              minlength="6"
            />
          </div>

          <div v-if="passwordError" class="mb-4 text-red-600 text-sm">
            {{ passwordError }}
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeResetPasswordDialog"
              class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
            >
              キャンセル
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              リセット
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const currentUser = computed(() => authStore.user)

const users = ref([])
const loading = ref(true)
const showEditDialog = ref(false)
const showResetPasswordDialog = ref(false)
const editingUser = ref({})
const resetPasswordUser = ref(null)
const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')

onMounted(() => {
  loadUsers()
})

async function loadUsers() {
  try {
    loading.value = true
    const response = await axios.get('/api/users')
    users.value = response.data
  } catch (error) {
    console.error('ユーザー一覧の取得に失敗しました:', error)
    alert('ユーザー一覧の取得に失敗しました')
  } finally {
    loading.value = false
  }
}

function openEditDialog(user) {
  editingUser.value = { ...user }
  showEditDialog.value = true
}

function closeEditDialog() {
  showEditDialog.value = false
  editingUser.value = {}
}

async function saveUser() {
  try {
    const updateData = {
      username: editingUser.value.username,
      email: editingUser.value.email,
      full_name: editingUser.value.full_name || null,
    }

    if (currentUser.value?.is_admin) {
      updateData.is_active = editingUser.value.is_active
    }

    await axios.put(`/api/users/${editingUser.value.id}`, updateData)
    await loadUsers()
    closeEditDialog()
    alert('ユーザー情報を更新しました')
  } catch (error) {
    console.error('ユーザー情報の更新に失敗しました:', error)
    alert(error.response?.data?.detail || 'ユーザー情報の更新に失敗しました')
  }
}

function openResetPasswordDialog(user) {
  resetPasswordUser.value = user
  newPassword.value = ''
  confirmPassword.value = ''
  passwordError.value = ''
  showResetPasswordDialog.value = true
}

function closeResetPasswordDialog() {
  showResetPasswordDialog.value = false
  resetPasswordUser.value = null
  newPassword.value = ''
  confirmPassword.value = ''
  passwordError.value = ''
}

async function resetPassword() {
  passwordError.value = ''

  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = 'パスワードが一致しません'
    return
  }

  if (newPassword.value.length < 6) {
    passwordError.value = 'パスワードは6文字以上で入力してください'
    return
  }

  try {
    await axios.post(`/api/users/${resetPasswordUser.value.id}/reset-password`, {
      new_password: newPassword.value
    })
    closeResetPasswordDialog()
    alert('パスワードをリセットしました')
  } catch (error) {
    console.error('パスワードのリセットに失敗しました:', error)
    passwordError.value = error.response?.data?.detail || 'パスワードのリセットに失敗しました'
  }
}

async function confirmDelete(user) {
  if (!confirm(`${user.username} を削除してもよろしいですか？この操作は取り消せません。`)) {
    return
  }

  try {
    await axios.delete(`/api/users/${user.id}`)
    await loadUsers()
    alert('ユーザーを削除しました')
  } catch (error) {
    console.error('ユーザーの削除に失敗しました:', error)
    alert(error.response?.data?.detail || 'ユーザーの削除に失敗しました')
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('ja-JP')
}
</script>
