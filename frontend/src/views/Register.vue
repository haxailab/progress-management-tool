<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-400 to-primary-600">
    <div class="bg-white p-8 rounded-lg shadow-2xl w-96">
      <h2 class="text-3xl font-bold text-center mb-6 text-gray-800">アカウント作成</h2>

      <form @submit.prevent="handleRegister">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            ユーザー名
          </label>
          <input
            v-model="username"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="username"
          />
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            メールアドレス
          </label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="email@example.com"
          />
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            氏名
          </label>
          <input
            v-model="fullName"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="山田 太郎"
          />
        </div>

        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            パスワード
          </label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="••••••••"
          />
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {{ error }}
        </div>

        <div v-if="success" class="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
          登録が完了しました。ログインページへ移動します...
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
        >
          {{ loading ? '登録中...' : '登録' }}
        </button>
      </form>

      <div class="mt-4 text-center">
        <router-link to="/login" class="text-primary-600 hover:text-primary-800 text-sm">
          既にアカウントをお持ちの方
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const fullName = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

const handleRegister = async () => {
  loading.value = true
  error.value = ''

  try {
    await authStore.register({
      username: username.value,
      email: email.value,
      full_name: fullName.value,
      password: password.value
    })

    success.value = true
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || '登録に失敗しました'
  } finally {
    loading.value = false
  }
}
</script>
