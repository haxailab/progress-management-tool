<template>
  <div class="p-8">
    <div class="mb-6">
      <button @click="goBack" class="text-primary-600 hover:text-primary-800 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        戻る
      </button>

      <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold text-gray-800">Wiki</h1>
        <button
          @click="showCreateModal = true"
          class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          新規ページ
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="pages.length === 0" class="text-center py-12 text-gray-500">
      Wikiページがありません
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="page in pages"
        :key="page.id"
        class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer"
        @click="viewPage(page)"
      >
        <div class="p-6">
          <h3 class="text-xl font-bold text-gray-800 mb-2">{{ page.title }}</h3>
          <p class="text-sm text-gray-500">
            作成者: {{ page.author?.username }} | {{ formatDate(page.created_at) }}
          </p>
        </div>
      </div>
    </div>

    <!-- ページ作成モーダル -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-screen overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-xl font-bold text-gray-800">新規Wikiページ</h2>
        </div>

        <form @submit.prevent="createPage" class="p-6">
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">タイトル</label>
            <input
              v-model="newPage.title"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div class="mb-6">
            <label class="block text-gray-700 text-sm font-bold mb-2">内容</label>
            <textarea
              v-model="newPage.content"
              rows="15"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
              placeholder="Markdown形式で入力できます"
            ></textarea>
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

    <!-- ページ詳細モーダル -->
    <div v-if="selectedPage" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-screen overflow-y-auto">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 class="text-xl font-bold text-gray-800">{{ selectedPage.title }}</h2>
          <button @click="selectedPage = null" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6">
          <div class="prose max-w-none" v-html="renderMarkdown(selectedPage.content)"></div>

          <div class="mt-6 pt-6 border-t border-gray-200 text-sm text-gray-500">
            作成者: {{ selectedPage.author?.username }} |
            作成: {{ formatDate(selectedPage.created_at) }} |
            更新: {{ formatDate(selectedPage.updated_at) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { marked } from 'marked'
import { format } from 'date-fns'

const route = useRoute()
const router = useRouter()

const pages = ref([])
const loading = ref(true)
const showCreateModal = ref(false)
const creating = ref(false)
const selectedPage = ref(null)

const newPage = ref({
  title: '',
  content: ''
})

const projectId = computed(() => parseInt(route.params.id))

onMounted(async () => {
  await fetchPages()
})

const fetchPages = async () => {
  try {
    const response = await api.wiki.list(projectId.value)
    pages.value = response.data
  } catch (err) {
    console.error('Failed to fetch wiki pages:', err)
  } finally {
    loading.value = false
  }
}

const createPage = async () => {
  creating.value = true

  try {
    await api.wiki.create({
      ...newPage.value,
      project_id: projectId.value
    })
    showCreateModal.value = false
    newPage.value = { title: '', content: '' }
    await fetchPages()
  } catch (err) {
    console.error('Failed to create wiki page:', err)
  } finally {
    creating.value = false
  }
}

const viewPage = (page) => {
  selectedPage.value = page
}

const renderMarkdown = (content) => {
  return marked(content || '')
}

const formatDate = (dateString) => {
  return format(new Date(dateString), 'yyyy/MM/dd HH:mm')
}

const goBack = () => {
  router.back()
}
</script>

<style>
.prose {
  @apply text-gray-700;
}

.prose h1 {
  @apply text-3xl font-bold mb-4;
}

.prose h2 {
  @apply text-2xl font-bold mb-3;
}

.prose h3 {
  @apply text-xl font-bold mb-2;
}

.prose p {
  @apply mb-4;
}

.prose ul {
  @apply list-disc list-inside mb-4;
}

.prose ol {
  @apply list-decimal list-inside mb-4;
}

.prose code {
  @apply bg-gray-100 px-1 py-0.5 rounded text-sm;
}

.prose pre {
  @apply bg-gray-100 p-4 rounded mb-4 overflow-x-auto;
}

.prose pre code {
  @apply bg-transparent p-0;
}
</style>
