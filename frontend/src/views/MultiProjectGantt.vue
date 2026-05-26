<template>
  <div class="p-6">
    <div class="mb-6">
      <h1 class="text-2xl font-bold mb-4">複数プロジェクト進捗管理</h1>

      <!-- プロジェクト選択 -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <h2 class="text-lg font-semibold mb-3">プロジェクトを選択</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <label
            v-for="project in availableProjects"
            :key="project.id"
            class="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50"
            :class="{ 'bg-blue-50 border-blue-500': selectedProjectIds.includes(project.id) }"
          >
            <input
              type="checkbox"
              :value="project.id"
              v-model="selectedProjectIds"
              class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            />
            <span class="ml-3">
              <span class="font-medium">{{ project.name }}</span>
              <span class="text-sm text-gray-500 ml-2">{{ project.key }}</span>
            </span>
          </label>
        </div>

        <div class="mt-4 flex justify-between items-center">
          <div class="text-sm text-gray-600">
            {{ selectedProjectIds.length }}個のプロジェクトを選択中
          </div>
          <button
            @click="loadIssues"
            :disabled="selectedProjectIds.length === 0"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            表示
          </button>
        </div>
      </div>

      <!-- 表示期間切り替え -->
      <div v-if="issues.length > 0" class="bg-white rounded-lg shadow p-4 mb-6">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold">表示期間</h2>
          <div class="flex space-x-2">
            <button
              @click="viewMode = 'day'"
              :class="[
                'px-4 py-2 rounded-md font-medium transition',
                viewMode === 'day' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              日毎
            </button>
            <button
              @click="viewMode = 'week'"
              :class="[
                'px-4 py-2 rounded-md font-medium transition',
                viewMode === 'week' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              週毎
            </button>
            <button
              @click="viewMode = 'month'"
              :class="[
                'px-4 py-2 rounded-md font-medium transition',
                viewMode === 'month' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              ]"
            >
              月毎
            </button>
          </div>
        </div>
      </div>

      <!-- 統計情報 -->
      <div v-if="issues.length > 0" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-gray-500">総課題数</div>
          <div class="text-2xl font-bold">{{ stats.total }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-gray-500">完了</div>
          <div class="text-2xl font-bold text-green-600">{{ stats.completed }}</div>
          <div class="text-xs text-gray-500">{{ stats.completionRate }}%</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-gray-500">進行中</div>
          <div class="text-2xl font-bold text-blue-600">{{ stats.inProgress }}</div>
        </div>
        <div class="bg-white rounded-lg shadow p-4">
          <div class="text-sm text-red-500">期限超過</div>
          <div class="text-2xl font-bold text-red-600">{{ stats.overdue }}</div>
        </div>
      </div>
    </div>

    <!-- ガントチャート -->
    <div v-if="loading" class="text-center py-8">
      読み込み中...
    </div>

    <div v-else-if="issues.length === 0 && selectedProjectIds.length > 0" class="text-center py-8 text-gray-500">
      選択したプロジェクトに課題がありません
    </div>

    <div v-else-if="issues.length > 0" class="bg-white rounded-lg shadow p-6 overflow-x-auto">
      <h2 class="text-lg font-semibold mb-4">統合ガントチャート</h2>

      <!-- 凡例 -->
      <div class="mb-4 flex flex-wrap gap-4 text-sm">
        <div class="flex items-center">
          <div class="w-4 h-4 bg-blue-500 rounded mr-2"></div>
          <span>未対応</span>
        </div>
        <div class="flex items-center">
          <div class="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
          <span>処理中</span>
        </div>
        <div class="flex items-center">
          <div class="w-4 h-4 bg-purple-500 rounded mr-2"></div>
          <span>レビュー</span>
        </div>
        <div class="flex items-center">
          <div class="w-4 h-4 bg-green-500 rounded mr-2"></div>
          <span>完了</span>
        </div>
        <div class="flex items-center">
          <div class="w-4 h-4 bg-red-500 rounded mr-2"></div>
          <span>期限超過</span>
        </div>
      </div>

      <div class="gantt-container" style="min-width: 800px;">
        <!-- ヘッダー（日付） -->
        <div class="flex border-b">
          <div class="w-80 p-2 font-semibold border-r bg-gray-50">課題</div>
          <div class="flex-1 flex">
            <div
              v-for="period in dateRange"
              :key="period.key"
              :class="[
                'flex-1 p-2 text-center text-xs border-r',
                { 'bg-blue-50': period.isCurrent },
                viewMode === 'day' ? 'min-w-[60px]' : viewMode === 'week' ? 'min-w-[100px]' : 'min-w-[120px]'
              ]"
            >
              <div class="font-semibold">{{ period.label }}</div>
              <div v-if="period.subLabel" class="text-gray-500">{{ period.subLabel }}</div>
            </div>
          </div>
        </div>

        <!-- 課題行（プロジェクトごとにグループ化） -->
        <div v-for="projectGroup in groupedIssues" :key="projectGroup.projectId">
          <!-- プロジェクト名ヘッダー -->
          <div class="flex border-b bg-gray-100">
            <div class="w-80 p-3 font-bold border-r">
              {{ projectGroup.projectName }} ({{ projectGroup.projectKey }})
            </div>
            <div class="flex-1"></div>
          </div>

          <!-- 課題 -->
          <div
            v-for="issue in projectGroup.issues"
            :key="issue.id"
            class="flex border-b hover:bg-gray-50"
          >
            <div class="w-80 p-2 border-r">
              <div class="font-medium text-sm">
                {{ projectGroup.projectKey }}-{{ issue.issue_number }}
              </div>
              <div class="text-xs text-gray-600 truncate">{{ issue.title }}</div>
              <div class="text-xs text-gray-500 mt-1">
                <span :class="getStatusColor(issue.status)">{{ issue.status }}</span>
                <span v-if="issue.assignee" class="ml-2">担当: {{ issue.assignee.username }}</span>
              </div>
            </div>
            <div class="flex-1 relative" style="height: 60px;">
              <!-- ガントバー -->
              <div
                v-if="issue.start_date && issue.due_date"
                class="absolute rounded"
                :style="getBarStyle(issue)"
                :class="getBarColor(issue)"
              >
                <div class="px-2 py-1 text-xs text-white truncate">
                  {{ issue.progress }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const availableProjects = ref([])
const selectedProjectIds = ref([])
const issues = ref([])
const loading = ref(false)
const projectsMap = ref({})
const viewMode = ref('week') // 'day', 'week', 'month'

onMounted(() => {
  loadProjects()
})

async function loadProjects() {
  try {
    const response = await axios.get('/api/projects')
    availableProjects.value = response.data
    // プロジェクトマップを作成
    projectsMap.value = {}
    response.data.forEach(project => {
      projectsMap.value[project.id] = project
    })
  } catch (error) {
    console.error('プロジェクト一覧の取得に失敗しました:', error)
    alert('プロジェクト一覧の取得に失敗しました')
  }
}

async function loadIssues() {
  if (selectedProjectIds.value.length === 0) {
    return
  }

  try {
    loading.value = true
    const projectIdsStr = selectedProjectIds.value.join(',')
    const response = await axios.get(`/api/issues/multi-project?project_ids=${projectIdsStr}`)
    issues.value = response.data
  } catch (error) {
    console.error('課題の取得に失敗しました:', error)
    alert(error.response?.data?.detail || '課題の取得に失敗しました')
  } finally {
    loading.value = false
  }
}

// プロジェクトごとにグループ化
const groupedIssues = computed(() => {
  const groups = {}

  issues.value.forEach(issue => {
    if (!groups[issue.project_id]) {
      const project = projectsMap.value[issue.project_id]
      groups[issue.project_id] = {
        projectId: issue.project_id,
        projectName: project?.name || 'Unknown',
        projectKey: project?.key || 'UNK',
        issues: []
      }
    }
    groups[issue.project_id].issues.push(issue)
  })

  return Object.values(groups)
})

// 統計情報
const stats = computed(() => {
  const total = issues.value.length
  const completed = issues.value.filter(i => i.status === '完了' || i.status === '終了').length
  const inProgress = issues.value.filter(i => i.status === '処理中').length
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const overdue = issues.value.filter(i => {
    if (!i.due_date || i.status === '完了' || i.status === '終了') return false
    const dueDate = new Date(i.due_date)
    return dueDate < today
  }).length

  const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0

  return {
    total,
    completed,
    inProgress,
    overdue,
    completionRate
  }
})

// 日付範囲の計算
const dateRange = computed(() => {
  if (issues.value.length === 0) return []

  let minDate = null
  let maxDate = null

  issues.value.forEach(issue => {
    if (issue.start_date) {
      const start = new Date(issue.start_date)
      if (!minDate || start < minDate) minDate = start
    }
    if (issue.due_date) {
      const due = new Date(issue.due_date)
      if (!maxDate || due > maxDate) maxDate = due
    }
  })

  if (!minDate || !maxDate) return []

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  if (viewMode.value === 'day') {
    return generateDayRange(minDate, maxDate, today)
  } else if (viewMode.value === 'week') {
    return generateWeekRange(minDate, maxDate, today)
  } else {
    return generateMonthRange(minDate, maxDate, today)
  }
})

function generateDayRange(minDate, maxDate, today) {
  // 前後に余裕を持たせる
  const start = new Date(minDate)
  start.setDate(start.getDate() - 7)
  const end = new Date(maxDate)
  end.setDate(end.getDate() + 7)

  const dates = []
  const current = new Date(start)
  while (current <= end) {
    const isCurrent = current.getTime() === today.getTime()
    dates.push({
      key: current.toISOString().split('T')[0],
      date: current.toISOString().split('T')[0],
      label: `${current.getMonth() + 1}/${current.getDate()}`,
      subLabel: ['日', '月', '火', '水', '木', '金', '土'][current.getDay()],
      isCurrent,
      startDate: new Date(current),
      endDate: new Date(current)
    })
    current.setDate(current.getDate() + 1)
  }
  return dates
}

function generateWeekRange(minDate, maxDate, today) {
  // 週の開始（月曜日）に調整
  const start = new Date(minDate)
  const startDay = start.getDay()
  const diff = startDay === 0 ? -6 : 1 - startDay
  start.setDate(start.getDate() + diff - 7) // 1週間前から

  const end = new Date(maxDate)
  end.setDate(end.getDate() + 14) // 2週間後まで

  const weeks = []
  const current = new Date(start)

  while (current <= end) {
    const weekStart = new Date(current)
    const weekEnd = new Date(current)
    weekEnd.setDate(weekEnd.getDate() + 6)

    // 現在の週かどうか
    const isCurrent = today >= weekStart && today <= weekEnd

    weeks.push({
      key: `week-${weekStart.toISOString().split('T')[0]}`,
      date: weekStart.toISOString().split('T')[0],
      label: `${weekStart.getMonth() + 1}/${weekStart.getDate()}`,
      subLabel: `～${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`,
      isCurrent,
      startDate: weekStart,
      endDate: weekEnd
    })

    current.setDate(current.getDate() + 7)
  }

  return weeks
}

function generateMonthRange(minDate, maxDate, today) {
  // 月の開始に調整
  const start = new Date(minDate)
  start.setDate(1)
  start.setMonth(start.getMonth() - 1) // 1ヶ月前から

  const end = new Date(maxDate)
  end.setMonth(end.getMonth() + 2) // 2ヶ月後まで

  const months = []
  const current = new Date(start)

  while (current <= end) {
    const monthStart = new Date(current.getFullYear(), current.getMonth(), 1)
    const monthEnd = new Date(current.getFullYear(), current.getMonth() + 1, 0)

    // 現在の月かどうか
    const isCurrent = today >= monthStart && today <= monthEnd

    months.push({
      key: `month-${current.getFullYear()}-${current.getMonth() + 1}`,
      date: monthStart.toISOString().split('T')[0],
      label: `${current.getFullYear()}年`,
      subLabel: `${current.getMonth() + 1}月`,
      isCurrent,
      startDate: monthStart,
      endDate: monthEnd
    })

    current.setMonth(current.getMonth() + 1)
  }

  return months
}

function getBarStyle(issue) {
  if (!issue.start_date || !issue.due_date || dateRange.value.length === 0) {
    return {}
  }

  const startDate = new Date(issue.start_date)
  startDate.setHours(0, 0, 0, 0)
  const dueDate = new Date(issue.due_date)
  dueDate.setHours(23, 59, 59, 999)

  const rangeStart = new Date(dateRange.value[0].startDate)
  rangeStart.setHours(0, 0, 0, 0)
  const rangeEnd = new Date(dateRange.value[dateRange.value.length - 1].endDate)
  rangeEnd.setHours(23, 59, 59, 999)

  const totalMs = rangeEnd - rangeStart
  const startOffsetMs = startDate - rangeStart
  const durationMs = dueDate - startDate

  const left = (startOffsetMs / totalMs) * 100
  const width = (durationMs / totalMs) * 100

  return {
    left: `${Math.max(0, left)}%`,
    width: `${Math.max(1, width)}%`,
    top: '10px'
  }
}

function getBarColor(issue) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dueDate = issue.due_date ? new Date(issue.due_date) : null

  // 期限超過
  if (dueDate && dueDate < today && issue.status !== '完了' && issue.status !== '終了') {
    return 'bg-red-500'
  }

  // ステータスによる色分け
  switch (issue.status) {
    case '完了':
    case '終了':
      return 'bg-green-500'
    case 'レビュー':
      return 'bg-purple-500'
    case '処理中':
      return 'bg-yellow-500'
    default:
      return 'bg-blue-500'
  }
}

function getStatusColor(status) {
  switch (status) {
    case '完了':
    case '終了':
      return 'text-green-600 font-semibold'
    case 'レビュー':
      return 'text-purple-600 font-semibold'
    case '処理中':
      return 'text-yellow-600 font-semibold'
    default:
      return 'text-blue-600 font-semibold'
  }
}
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
