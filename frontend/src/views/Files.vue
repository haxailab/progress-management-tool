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
        <h1 class="text-3xl font-bold text-gray-800">ファイル</h1>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <div class="text-center py-12 text-gray-500">
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        <p class="text-lg font-medium mb-2">ファイル管理機能</p>
        <p class="text-sm">この機能は今後実装予定です</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  router.back()
}
</script>
