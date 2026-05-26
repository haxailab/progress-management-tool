<template>
  <div class="p-8">
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="issue" class="max-w-5xl mx-auto">
      <!-- ヘッダー -->
      <div class="mb-6">
        <button @click="goBack" class="text-primary-600 hover:text-primary-800 mb-4 flex items-center">
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          戻る
        </button>

        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="text-sm text-gray-500 mb-2">
              課題 {{ issue.project?.key }}-{{ issue.issue_number }}
            </div>
            <h1 class="text-3xl font-bold text-gray-800 mb-4">{{ issue.title }}</h1>

            <div class="flex items-center space-x-4">
              <span class="px-3 py-1 rounded-full text-sm font-medium"
                :class="getStatusClass(issue.status)">
                {{ issue.status }}
              </span>
              <span class="px-3 py-1 rounded-full text-sm font-medium"
                :class="getPriorityClass(issue.priority)">
                {{ issue.priority }}
              </span>
            </div>
          </div>

          <button
            @click="showEditModal = true"
            class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg"
          >
            編集
          </button>
        </div>
      </div>

      <!-- メインコンテンツ -->
      <div class="grid grid-cols-3 gap-6">
        <!-- 左側: 詳細情報 -->
        <div class="col-span-2 space-y-6">
          <!-- 説明 -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-bold text-gray-800 mb-4">説明</h2>
            <div class="text-gray-700 whitespace-pre-wrap">
              {{ issue.description || '説明なし' }}
            </div>
          </div>

          <!-- コメント -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-bold text-gray-800 mb-4">コメント</h2>

            <div v-if="comments.length === 0" class="text-gray-500 text-sm mb-4">
              コメントはまだありません
            </div>

            <div v-else class="space-y-4 mb-4">
              <div
                v-for="comment in comments"
                :key="comment.id"
                class="border border-gray-200 rounded-lg p-4"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center">
                    <span class="font-medium text-gray-800">{{ comment.author?.username }}</span>
                    <span class="ml-2 text-sm text-gray-500">
                      {{ formatDate(comment.created_at) }}
                    </span>
                  </div>
                </div>
                <div class="text-gray-700 whitespace-pre-wrap">{{ comment.content }}</div>
              </div>
            </div>

            <form @submit.prevent="addComment" class="mt-4">
              <textarea
                v-model="newComment"
                rows="3"
                placeholder="コメントを入力..."
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              ></textarea>
              <div class="mt-2 flex justify-end">
                <button
                  type="submit"
                  :disabled="!newComment.trim() || submitting"
                  class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50"
                >
                  コメントを追加
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- 右側: メタ情報 -->
        <div class="col-span-1">
          <div class="bg-white rounded-lg shadow p-6 space-y-4">
            <div>
              <h3 class="text-sm font-medium text-gray-500">担当者</h3>
              <p class="mt-1 text-gray-900">{{ issue.assignee?.username || '未割り当て' }}</p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500">作成者</h3>
              <p class="mt-1 text-gray-900">{{ issue.creator?.username }}</p>
            </div>

            <div v-if="issue.milestone">
              <h3 class="text-sm font-medium text-gray-500">マイルストーン</h3>
              <p class="mt-1 text-gray-900">{{ issue.milestone.name }}</p>
            </div>

            <div v-if="issue.category">
              <h3 class="text-sm font-medium text-gray-500">カテゴリ</h3>
              <p class="mt-1 text-gray-900">{{ issue.category.name }}</p>
            </div>

            <div v-if="issue.start_date">
              <h3 class="text-sm font-medium text-gray-500">開始日</h3>
              <p class="mt-1 text-gray-900">{{ issue.start_date }}</p>
            </div>

            <div v-if="issue.due_date">
              <h3 class="text-sm font-medium text-gray-500">期限</h3>
              <p class="mt-1 text-gray-900">{{ issue.due_date }}</p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500">作成日時</h3>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(issue.created_at) }}</p>
            </div>

            <div>
              <h3 class="text-sm font-medium text-gray-500">更新日時</h3>
              <p class="mt-1 text-sm text-gray-900">{{ formatDate(issue.updated_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 編集モーダル -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-screen overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">課題を編集</h2>
        </div>

        <form @submit.prevent="updateIssue" class="p-6">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">タイトル</label>
            <input
              v-model="editForm.title"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">説明</label>
            <textarea
              v-model="editForm.description"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">ステータス</label>
              <select
                v-model="editForm.status"
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
              <label class="block text-gray-700 text-sm font-bold mb-2">優先度</label>
              <select
                v-model="editForm.priority"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="低">低</option>
                <option value="中">中</option>
                <option value="高">高</option>
                <option value="最重要">最重要</option>
              </select>
            </div>
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="showEditModal = false"
              class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              キャンセル
            </button>
            <button
              type="submit"
              :disabled="updating"
              class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50"
            >
              {{ updating ? '更新中...' : '更新' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { format } from 'date-fns'

const route = useRoute()
const router = useRouter()

const issue = ref(null)
const comments = ref([])
const loading = ref(true)
const showEditModal = ref(false)
const updating = ref(false)
const submitting = ref(false)
const newComment = ref('')

const editForm = ref({
  title: '',
  description: '',
  status: '',
  priority: ''
})

const issueId = ref(parseInt(route.params.id))

onMounted(async () => {
  await fetchIssue()
  await fetchComments()
})

const fetchIssue = async () => {
  try {
    const response = await api.issues.get(issueId.value)
    issue.value = response.data
    editForm.value = {
      title: issue.value.title,
      description: issue.value.description,
      status: issue.value.status,
      priority: issue.value.priority
    }
  } catch (err) {
    console.error('Failed to fetch issue:', err)
  } finally {
    loading.value = false
  }
}

const fetchComments = async () => {
  try {
    const response = await api.comments.list(issueId.value)
    comments.value = response.data
  } catch (err) {
    console.error('Failed to fetch comments:', err)
  }
}

const updateIssue = async () => {
  updating.value = true

  try {
    await api.issues.update(issueId.value, editForm.value)
    showEditModal.value = false
    await fetchIssue()
  } catch (err) {
    console.error('Failed to update issue:', err)
  } finally {
    updating.value = false
  }
}

const addComment = async () => {
  if (!newComment.value.trim()) return

  submitting.value = true

  try {
    await api.comments.create({
      issue_id: issueId.value,
      content: newComment.value
    })
    newComment.value = ''
    await fetchComments()
  } catch (err) {
    console.error('Failed to add comment:', err)
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
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
