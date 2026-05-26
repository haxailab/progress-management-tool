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
        <h1 class="text-3xl font-bold text-gray-800">ガントチャート</h1>
        <div class="flex space-x-2">
          <button
            v-for="mode in viewModes"
            :key="mode.value"
            @click="changeViewMode(mode.value)"
            class="px-3 py-1 rounded text-sm"
            :class="currentViewMode === mode.value ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
          >
            {{ mode.label }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else class="bg-white rounded-lg shadow p-6">
      <div v-if="issuesWithDates.length === 0" class="text-center py-8 text-gray-500">
        開始日と期限が設定された課題がありません
      </div>

      <div v-else>
        <!-- ガントチャート -->
        <div ref="ganttContainer" class="gantt-container"></div>

        <!-- 凡例 -->
        <div class="mt-6 flex items-center space-x-6">
          <div class="flex items-center">
            <div class="w-4 h-4 bg-gray-400 rounded mr-2"></div>
            <span class="text-sm text-gray-600">未対応</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 bg-blue-400 rounded mr-2"></div>
            <span class="text-sm text-gray-600">処理中</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 bg-yellow-400 rounded mr-2"></div>
            <span class="text-sm text-gray-600">レビュー</span>
          </div>
          <div class="flex items-center">
            <div class="w-4 h-4 bg-green-400 rounded mr-2"></div>
            <span class="text-sm text-gray-600">完了</span>
          </div>
        </div>

        <!-- 依存関係管理パネル -->
        <div class="mt-6 border-t pt-6">
          <h3 class="text-lg font-bold text-gray-800 mb-4">依存関係の追加</h3>
          <div class="grid grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">前提タスク</label>
              <select
                v-model="newDependency.source_issue_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option :value="null">選択してください</option>
                <option v-for="issue in issuesWithDates" :key="issue.id" :value="issue.id">
                  {{ issue.title }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">依存タスク</label>
              <select
                v-model="newDependency.target_issue_id"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option :value="null">選択してください</option>
                <option v-for="issue in issuesWithDates" :key="issue.id" :value="issue.id">
                  {{ issue.title }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">依存タイプ</label>
              <select
                v-model="newDependency.dependency_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="finish-to-start">終了→開始 (FS)</option>
                <option value="start-to-start">開始→開始 (SS)</option>
                <option value="finish-to-finish">終了→終了 (FF)</option>
                <option value="start-to-finish">開始→終了 (SF)</option>
              </select>
            </div>

            <div class="flex items-end">
              <button
                @click="addDependency"
                :disabled="!newDependency.source_issue_id || !newDependency.target_issue_id"
                class="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                追加
              </button>
            </div>
          </div>

          <!-- 既存の依存関係リスト -->
          <div v-if="dependencies.length > 0" class="mt-4">
            <h4 class="text-sm font-medium text-gray-700 mb-2">設定済み依存関係</h4>
            <div class="space-y-2">
              <div
                v-for="dep in dependencies"
                :key="dep.id"
                class="flex items-center justify-between bg-gray-50 px-4 py-2 rounded"
              >
                <span class="text-sm">
                  {{ getIssueTitle(dep.source_issue_id) }}
                  <span class="text-gray-500 mx-2">→</span>
                  {{ getIssueTitle(dep.target_issue_id) }}
                  <span class="text-xs text-gray-500 ml-2">({{ getDependencyTypeLabel(dep.dependency_type) }})</span>
                </span>
                <button
                  @click="removeDependency(dep.id)"
                  class="text-red-600 hover:text-red-800"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import Gantt from 'frappe-gantt'

const route = useRoute()
const router = useRouter()

const issues = ref([])
const dependencies = ref([])
const loading = ref(true)
const ganttContainer = ref(null)
const ganttInstance = ref(null)
const currentViewMode = ref('Day')
const updating = ref(false)

const viewModes = [
  { label: '日', value: 'Day' },
  { label: '週', value: 'Week' },
  { label: '月', value: 'Month' }
]

const newDependency = ref({
  source_issue_id: null,
  target_issue_id: null,
  dependency_type: 'finish-to-start'
})

const projectId = computed(() => parseInt(route.params.id))

const issuesWithDates = computed(() => {
  return issues.value.filter(issue => issue.start_date && issue.due_date)
})

onMounted(async () => {
  await Promise.all([
    fetchIssues(),
    fetchDependencies()
  ])
  await nextTick()
  initGantt()
})

onBeforeUnmount(() => {
  // Ganttインスタンスをクリーンアップ
  if (ganttInstance.value) {
    ganttInstance.value = null
  }
})

const fetchIssues = async () => {
  try {
    const response = await api.issues.list(projectId.value)
    issues.value = response.data
  } catch (err) {
    console.error('Failed to fetch issues:', err)
  } finally {
    loading.value = false
  }
}

const fetchDependencies = async () => {
  try {
    const response = await api.dependencies.list(projectId.value)
    dependencies.value = response.data
  } catch (err) {
    console.error('Failed to fetch dependencies:', err)
  }
}

const initGantt = () => {
  console.log('initGantt called')
  console.log('ganttContainer:', ganttContainer.value)
  console.log('issuesWithDates:', issuesWithDates.value)

  if (!ganttContainer.value) {
    console.error('ganttContainer not found')
    return
  }

  if (issuesWithDates.value.length === 0) {
    console.log('No issues with dates')
    return
  }

  try {
    console.log('Mapping tasks...')
    const tasks = issuesWithDates.value.map(issue => {
      console.log('Processing issue:', issue)
      const deps = getDependenciesForIssue(issue.id)

      // 日付文字列を文字列形式で保持（YYYY-MM-DD）
      const task = {
        id: issue.id.toString(),
        name: issue.title,
        start: issue.start_date, // 文字列のまま
        end: issue.due_date,     // 文字列のまま
        progress: issue.progress || 0,
        dependencies: deps || '',
        custom_class: getCustomClass(issue.status)
      }
      console.log('Created task:', task)
      return task
    })

    console.log('All tasks created:', tasks)

    console.log('Creating Gantt instance...')
    ganttInstance.value = new Gantt(ganttContainer.value, tasks, {
      view_mode: 'Day',
      readonly: true, // ドラッグを無効化
      on_click: (task) => {
        const issueId = parseInt(task.id)
        router.push(`/issues/${issueId}`)
      }
    })
    console.log('Gantt instance created successfully')
  } catch (error) {
    console.error('Failed to initialize Gantt:', error)
    console.error('Error stack:', error.stack)
    alert('ガントチャートの初期化に失敗しました: ' + error.message)
  }
}

const changeViewMode = (mode) => {
  if (ganttInstance.value) {
    ganttInstance.value.change_view_mode(mode)
    currentViewMode.value = mode
  }
}

const getDependenciesForIssue = (issueId) => {
  const deps = dependencies.value
    .filter(dep => dep.target_issue_id === issueId)
    .map(dep => dep.source_issue_id.toString())
  return deps.length > 0 ? deps.join(',') : ''
}

const getCustomClass = (status) => {
  const classes = {
    '未対応': 'bar-gray',
    '処理中': 'bar-blue',
    'レビュー': 'bar-yellow',
    '完了': 'bar-green',
    '終了': 'bar-dark'
  }
  return classes[status] || 'bar-gray'
}

const updateIssueDates = async (issueId, start, end) => {
  if (updating.value) {
    console.log('Already updating, skipping...')
    return
  }

  updating.value = true
  try {
    const startDate = start.toISOString().split('T')[0]
    const endDate = end.toISOString().split('T')[0]

    console.log(`Updating issue ${issueId}: ${startDate} - ${endDate}`)

    await api.issues.update(issueId, {
      start_date: startDate,
      due_date: endDate
    })

    // 課題リストを更新
    const issue = issues.value.find(i => i.id === issueId)
    if (issue) {
      issue.start_date = startDate
      issue.due_date = endDate
    }
  } catch (err) {
    console.error('Failed to update dates:', err)
    alert('日付の更新に失敗しました')
  } finally {
    updating.value = false
  }
}

const updateIssueProgress = async (issueId, progress) => {
  if (updating.value) {
    console.log('Already updating, skipping...')
    return
  }

  updating.value = true
  try {
    console.log(`Updating progress for issue ${issueId}: ${progress}%`)

    await api.issues.update(issueId, { progress })

    // 課題リストを更新
    const issue = issues.value.find(i => i.id === issueId)
    if (issue) {
      issue.progress = progress
    }
  } catch (err) {
    console.error('Failed to update progress:', err)
    alert('進捗の更新に失敗しました')
  } finally {
    updating.value = false
  }
}

const addDependency = async () => {
  if (!newDependency.value.source_issue_id || !newDependency.value.target_issue_id) return

  try {
    await api.dependencies.create(newDependency.value)
    await fetchDependencies()
    newDependency.value = {
      source_issue_id: null,
      target_issue_id: null,
      dependency_type: 'finish-to-start'
    }
    // ガントチャートを再描画
    initGantt()
  } catch (err) {
    console.error('Failed to add dependency:', err)
    alert(err.response?.data?.detail || '依存関係の追加に失敗しました')
  }
}

const removeDependency = async (dependencyId) => {
  if (!confirm('この依存関係を削除しますか？')) return

  try {
    await api.dependencies.delete(dependencyId)
    await fetchDependencies()
    // ガントチャートを再描画
    initGantt()
  } catch (err) {
    console.error('Failed to remove dependency:', err)
    alert('依存関係の削除に失敗しました')
  }
}

const getIssueTitle = (issueId) => {
  const issue = issues.value.find(i => i.id === issueId)
  return issue ? issue.title : '不明'
}

const getDependencyTypeLabel = (type) => {
  const labels = {
    'finish-to-start': '終了→開始',
    'start-to-start': '開始→開始',
    'finish-to-finish': '終了→終了',
    'start-to-finish': '開始→終了'
  }
  return labels[type] || type
}

const goBack = () => {
  router.back()
}
</script>

<style>
.gantt-container {
  overflow-x: auto;
  min-height: 400px;
}

/* ステータス別のバーの色 */
:deep(.bar-gray .bar) {
  fill: #9ca3af !important;
}

:deep(.bar-blue .bar) {
  fill: #60a5fa !important;
}

:deep(.bar-yellow .bar) {
  fill: #fbbf24 !important;
}

:deep(.bar-green .bar) {
  fill: #4ade80 !important;
}

:deep(.bar-dark .bar) {
  fill: #4b5563 !important;
}

/* 進捗バーのスタイル */
:deep(.bar-progress) {
  fill: rgba(0, 0, 0, 0.3) !important;
}

/* ガントチャート全体のスタイル調整 */
:deep(.gantt) {
  font-family: inherit;
}

:deep(.gantt .grid-header) {
  fill: #f9fafb;
  stroke: #e5e7eb;
}

:deep(.gantt .grid-row) {
  fill: #ffffff;
}

:deep(.gantt .grid-row:nth-child(even)) {
  fill: #f9fafb;
}

:deep(.gantt .today-highlight) {
  fill: #dbeafe;
}

:deep(.gantt .arrow) {
  stroke: #6b7280;
  stroke-width: 1.5;
}

/* Frappe Gantt Base Styles */
:deep(.gantt) {
  overflow: auto;
}

:deep(.gantt .grid) {
  stroke: #e0e0e0;
  stroke-width: 1;
}

:deep(.gantt .tick) {
  stroke: #e0e0e0;
  stroke-width: 0.2;
}

:deep(.gantt .date) {
  fill: #000;
  font-size: 12px;
}

:deep(.gantt .bar-wrapper) {
  cursor: pointer;
}

:deep(.gantt .bar) {
  fill: #60a5fa;
  stroke: #3b82f6;
  stroke-width: 1;
  transition: opacity 0.3s;
}

:deep(.gantt .bar:hover) {
  opacity: 0.8;
}

:deep(.gantt .handle) {
  fill: #3b82f6;
  opacity: 0;
  cursor: ew-resize;
}

:deep(.gantt .bar-wrapper:hover .handle) {
  opacity: 1;
}

:deep(.gantt .bar-label) {
  fill: #fff;
  font-size: 11px;
  font-weight: 500;
  text-anchor: middle;
  pointer-events: none;
}

:deep(.gantt .bar-progress) {
  fill: rgba(0, 0, 0, 0.15);
}

:deep(.gantt .lower-text) {
  font-size: 10px;
  fill: #666;
  text-anchor: middle;
}

:deep(.gantt .upper-text) {
  font-size: 12px;
  fill: #000;
  text-anchor: middle;
  font-weight: 600;
}

:deep(.gantt .pointer) {
  fill: red;
  stroke: red;
}
</style>
