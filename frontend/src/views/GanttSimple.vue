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
            @click="currentViewMode = mode.value"
            class="px-4 py-2 rounded text-sm font-medium"
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
        <!-- 凡例 -->
        <div class="mb-4 flex items-center space-x-6">
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
          <div class="ml-4 text-xs text-gray-500">
            濃い色：完了済み / 薄い色：未完了
          </div>
        </div>

        <!-- スクロール可能なガントチャート -->
        <div class="overflow-x-auto border" style="max-height: 70vh;" ref="ganttScroll">
        <!-- 日表示 -->
        <table v-if="currentViewMode === 'day'" class="border-collapse" style="min-width: 3000px;">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase border sticky left-0 bg-gray-50 z-10">課題</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase border sticky bg-gray-50 z-10" style="left: 120px;">進捗</th>
              <th
                v-for="month in monthHeaders"
                :key="month.key"
                :colspan="month.colspan"
                class="px-4 py-2 text-xs font-medium text-gray-500 uppercase border text-center"
              >
                {{ month.label }}
              </th>
            </tr>
            <tr class="bg-gray-50">
              <th class="border sticky left-0 bg-gray-50 z-10"></th>
              <th class="border sticky bg-gray-50 z-10" style="left: 120px;"></th>
              <th
                v-for="col in dateColumns"
                :key="col.key"
                class="px-1 py-1 text-xs text-center border min-w-[30px]"
                :class="{ 'bg-blue-50': col.isToday }"
              >
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="issue in issuesWithDates"
              :key="issue.id"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-2 border text-sm font-medium sticky left-0 bg-white hover:bg-gray-50 z-10">
                {{ issue.title }}
              </td>
              <td class="px-4 py-2 border text-sm text-center sticky bg-white hover:bg-gray-50 z-10" style="left: 120px;">{{ issue.progress || 0 }}%</td>
              <td
                v-for="col in dateColumns"
                :key="col.key"
                class="p-0 border relative"
              >
                <div
                  v-if="isDateInRange(issue, col)"
                  class="h-8 cursor-pointer relative"
                  :class="getCellProgressClass(issue, col)"
                  @click="openEditModal(issue)"
                  :title="`${issue.title} - ${issue.progress || 0}%`"
                >
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 週表示 -->
        <table v-if="currentViewMode === 'week'" class="border-collapse" style="min-width: 2500px;">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase border sticky left-0 bg-gray-50 z-10">課題</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase border sticky bg-gray-50 z-10" style="left: 120px;">進捗</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase border" :colspan="dateColumns.length">
                {{ currentMonth }}
              </th>
            </tr>
            <tr class="bg-gray-50">
              <th class="border sticky left-0 bg-gray-50 z-10"></th>
              <th class="border sticky bg-gray-50 z-10" style="left: 120px;"></th>
              <th
                v-for="col in dateColumns"
                :key="col.key"
                class="px-2 py-1 text-xs text-center border min-w-[60px]"
              >
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="issue in issuesWithDates"
              :key="issue.id"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-2 border text-sm font-medium sticky left-0 bg-white hover:bg-gray-50 z-10">
                {{ issue.title }}
              </td>
              <td class="px-4 py-2 border text-sm text-center sticky bg-white hover:bg-gray-50 z-10" style="left: 120px;">{{ issue.progress || 0 }}%</td>
              <td
                v-for="col in dateColumns"
                :key="col.key"
                class="p-0 border relative"
              >
                <div
                  v-if="isDateInRange(issue, col)"
                  class="h-8 cursor-pointer relative"
                  :class="getCellProgressClass(issue, col)"
                  @click="openEditModal(issue)"
                  :title="`${issue.title} - ${issue.progress || 0}%`"
                >
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 月表示 -->
        <table v-if="currentViewMode === 'month'" class="border-collapse" style="min-width: 1600px;">
          <thead>
            <tr class="bg-gray-50">
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase border sticky left-0 bg-gray-50 z-10">課題</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase border sticky bg-gray-50 z-10" style="left: 120px;">進捗</th>
              <th
                v-for="col in dateColumns"
                :key="col.key"
                class="px-4 py-2 text-xs font-medium text-gray-500 uppercase border text-center min-w-[100px]"
              >
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="issue in issuesWithDates"
              :key="issue.id"
              class="hover:bg-gray-50"
            >
              <td class="px-4 py-2 border text-sm font-medium sticky left-0 bg-white hover:bg-gray-50 z-10">
                {{ issue.title }}
              </td>
              <td class="px-4 py-2 border text-sm text-center sticky bg-white hover:bg-gray-50 z-10" style="left: 120px;">{{ issue.progress || 0 }}%</td>
              <td
                v-for="col in dateColumns"
                :key="col.key"
                class="p-0 border relative"
              >
                <div
                  v-if="isDateInRange(issue, col)"
                  class="h-8 cursor-pointer relative"
                  :class="getCellProgressClass(issue, col)"
                  @click="openEditModal(issue)"
                  :title="`${issue.title} - ${issue.progress || 0}%`"
                >
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        </div>

        <!-- タスク追加フォーム（スクロール領域の外） -->
        <div class="mt-6 border-t pt-6">
          <h3 class="text-lg font-bold text-gray-800 mb-4">新規タスクを追加</h3>

          <form @submit.prevent="addIssue" class="space-y-4">
            <div class="grid grid-cols-6 gap-4">
              <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">タイトル *</label>
                <input
                  v-model="newIssue.title"
                  type="text"
                  required
                  placeholder="タスク名を入力"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">開始日 *</label>
                <input
                  v-model="newIssue.start_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">期限 *</label>
                <input
                  v-model="newIssue.due_date"
                  type="date"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">担当者</label>
                <select
                  v-model="newIssue.assignee_id"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option :value="null">未割り当て</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.username }}
                  </option>
                </select>
              </div>

              <div class="flex items-end">
                <button
                  type="submit"
                  :disabled="creating"
                  class="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50 flex items-center justify-center"
                >
                  <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  {{ creating ? '追加中...' : '追加' }}
                </button>
              </div>
            </div>

            <div v-if="createError" class="p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
              {{ createError }}
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 編集モーダル -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 class="text-xl font-bold text-gray-800">課題を編集</h2>
          <button @click="showEditModal = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="updateIssue" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">タイトル</label>
            <input
              v-model="editForm.title"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              readonly
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">開始日</label>
              <input
                v-model="editForm.start_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">期限</label>
              <input
                v-model="editForm.due_date"
                type="date"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">進捗率: {{ editForm.progress }}%</label>
            <input
              v-model.number="editForm.progress"
              type="range"
              min="0"
              max="100"
              step="5"
              class="w-full"
            />
          </div>

          <div class="flex justify-end space-x-3 pt-4">
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
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, eachWeekOfInterval, startOfWeek, endOfWeek, addMonths, isSameDay, isWithinInterval, parseISO } from 'date-fns'

const route = useRoute()
const router = useRouter()

const issues = ref([])
const users = ref([])
const loading = ref(true)
const currentViewMode = ref('day')
const showEditModal = ref(false)
const updating = ref(false)
const creating = ref(false)
const ganttScroll = ref(null)
const createError = ref('')

const viewModes = [
  { label: '日', value: 'day' },
  { label: '週', value: 'week' },
  { label: '月', value: 'month' }
]

const editForm = ref({
  id: null,
  title: '',
  start_date: '',
  due_date: '',
  progress: 0
})

const newIssue = ref({
  title: '',
  start_date: '',
  due_date: '',
  assignee_id: null,
  status: '未対応',
  priority: '中',
  progress: 0
})

const projectId = computed(() => parseInt(route.params.id))

const issuesWithDates = computed(() => {
  return issues.value.filter(issue => issue.start_date && issue.due_date)
})

const currentMonth = computed(() => {
  if (dateColumns.value.length === 0) return ''

  const firstCol = dateColumns.value[0]
  const lastCol = dateColumns.value[dateColumns.value.length - 1]

  if (currentViewMode.value === 'day') {
    return `${format(firstCol.date, 'yyyy年M月')} - ${format(lastCol.date, 'M月')}`
  } else if (currentViewMode.value === 'week') {
    return `${format(firstCol.start, 'yyyy年M月')} - ${format(lastCol.end, 'M月')}`
  } else {
    return `${firstCol.label} - ${lastCol.label.split('年')[1]}`
  }
})

const monthHeaders = computed(() => {
  if (currentViewMode.value !== 'day' || dateColumns.value.length === 0) return []

  const headers = []
  let currentMonth = null
  let colspan = 0

  dateColumns.value.forEach((col, index) => {
    const month = format(col.date, 'yyyy-MM')

    if (month !== currentMonth) {
      if (currentMonth !== null) {
        headers.push({
          key: currentMonth,
          label: format(parseISO(currentMonth + '-01'), 'yyyy年M月'),
          colspan: colspan
        })
      }
      currentMonth = month
      colspan = 1
    } else {
      colspan++
    }

    // 最後の列
    if (index === dateColumns.value.length - 1) {
      headers.push({
        key: currentMonth,
        label: format(parseISO(currentMonth + '-01'), 'yyyy年M月'),
        colspan: colspan
      })
    }
  })

  return headers
})

const dateColumns = computed(() => {
  const now = new Date()

  // タスクの最小開始日と最大終了日を取得
  let minDate = now
  let maxDate = now

  if (issuesWithDates.value.length > 0) {
    const dates = issuesWithDates.value.map(issue => ({
      start: parseISO(issue.start_date),
      end: parseISO(issue.due_date)
    }))

    minDate = new Date(Math.min(...dates.map(d => d.start)))
    maxDate = new Date(Math.max(...dates.map(d => d.end)))
  }

  if (currentViewMode.value === 'day') {
    // 最小日の10日前から最大日の10日後まで
    const start = new Date(minDate)
    start.setDate(start.getDate() - 10)
    const end = new Date(maxDate)
    end.setDate(end.getDate() + 10)

    const days = eachDayOfInterval({ start, end })
    return days.map(day => ({
      key: format(day, 'yyyy-MM-dd'),
      label: format(day, 'd'),
      date: day,
      isToday: isSameDay(day, now)
    }))
  } else if (currentViewMode.value === 'week') {
    // 最小日の10週前から最大日の10週後まで
    const start = new Date(minDate)
    start.setDate(start.getDate() - 70) // 10週 = 70日
    const end = new Date(maxDate)
    end.setDate(end.getDate() + 70)

    const weeks = eachWeekOfInterval({ start, end }, { weekStartsOn: 1 })
    return weeks.map((weekStart) => {
      const weekEnd = endOfWeek(weekStart, { weekStartsOn: 1 })
      return {
        key: format(weekStart, 'yyyy-MM-dd'),
        label: `${format(weekStart, 'M/d')}-${format(weekEnd, 'd')}`,
        start: weekStart,
        end: weekEnd,
        isToday: isWithinInterval(now, { start: weekStart, end: weekEnd })
      }
    })
  } else {
    // 月表示：最小日の10ヶ月前から最大日の10ヶ月後まで
    const startMonth = addMonths(startOfMonth(minDate), -10)
    const endMonth = addMonths(endOfMonth(maxDate), 10)

    const monthCount = Math.ceil((endMonth - startMonth) / (1000 * 60 * 60 * 24 * 30)) + 1

    return Array.from({ length: monthCount }, (_, i) => {
      const month = addMonths(startMonth, i)
      const monthStart = startOfMonth(month)
      const monthEnd = endOfMonth(month)
      return {
        key: format(month, 'yyyy-MM'),
        label: format(month, 'yyyy年M月'),
        start: monthStart,
        end: monthEnd,
        isToday: isWithinInterval(now, { start: monthStart, end: monthEnd })
      }
    })
  }
})

onMounted(async () => {
  await Promise.all([
    fetchIssues(),
    fetchUsers()
  ])
  scrollToToday()
})

const scrollToToday = () => {
  setTimeout(() => {
    if (!ganttScroll.value) return

    // 今日の日付のインデックスを探す
    const todayIndex = dateColumns.value.findIndex(col => col.isToday)

    if (todayIndex !== -1) {
      let scrollPosition = 0

      if (currentViewMode.value === 'day') {
        // 各セルの幅を30pxと仮定
        scrollPosition = todayIndex * 30 - 200
      } else if (currentViewMode.value === 'week') {
        // 各セルの幅を60pxと仮定
        scrollPosition = todayIndex * 60 - 200
      } else if (currentViewMode.value === 'month') {
        // 各セルの幅を100pxと仮定
        scrollPosition = todayIndex * 100 - 200
      }

      ganttScroll.value.scrollLeft = Math.max(0, scrollPosition)
    }
  }, 100)
}

// 表示モードが変更されたら再スクロール
watch(currentViewMode, () => {
  scrollToToday()
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

const fetchUsers = async () => {
  try {
    const response = await api.users.list()
    users.value = response.data
  } catch (err) {
    console.error('Failed to fetch users:', err)
  }
}

const isDateInRange = (issue, col) => {
  const start = parseISO(issue.start_date)
  const end = parseISO(issue.due_date)

  if (currentViewMode.value === 'day') {
    return isWithinInterval(col.date, { start, end })
  } else {
    // 週・月表示：期間が重なっているか
    return (start <= col.end && end >= col.start)
  }
}

const getCellProgressClass = (issue, col) => {
  const start = parseISO(issue.start_date)
  const end = parseISO(issue.due_date)
  const progress = issue.progress || 0

  // タスクの全期間（日数）
  const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1

  // 進捗に基づいて、何日分が完了しているか
  const completedDays = Math.ceil((totalDays * progress) / 100)

  // このセルが開始から何日目か
  let dayIndex
  if (currentViewMode.value === 'day') {
    dayIndex = Math.ceil((col.date - start) / (1000 * 60 * 60 * 24))
  } else {
    // 週・月表示の場合は期間の中間点を使用
    const colMid = new Date((col.start.getTime() + col.end.getTime()) / 2)
    dayIndex = Math.ceil((colMid - start) / (1000 * 60 * 60 * 24))
  }

  // このセルは完了済みか、未完了か（0%の場合は全て未完了）
  const isCompleted = progress > 0 && dayIndex < completedDays

  // ステータスに応じた色
  const statusColors = {
    '未対応': isCompleted ? 'bg-gray-600' : 'bg-gray-400',
    '処理中': isCompleted ? 'bg-blue-600' : 'bg-blue-400',
    'レビュー': isCompleted ? 'bg-yellow-600' : 'bg-yellow-400',
    '完了': isCompleted ? 'bg-green-600' : 'bg-green-400',
    '終了': isCompleted ? 'bg-gray-700' : 'bg-gray-600'
  }

  return statusColors[issue.status] || (isCompleted ? 'bg-gray-600' : 'bg-gray-400')
}

const openEditModal = (issue) => {
  editForm.value = {
    id: issue.id,
    title: issue.title,
    start_date: issue.start_date,
    due_date: issue.due_date,
    progress: issue.progress || 0
  }
  showEditModal.value = true
}

const updateIssue = async () => {
  updating.value = true
  try {
    await api.issues.update(editForm.value.id, {
      start_date: editForm.value.start_date,
      due_date: editForm.value.due_date,
      progress: editForm.value.progress
    })

    // ローカルの課題を更新
    const issue = issues.value.find(i => i.id === editForm.value.id)
    if (issue) {
      issue.start_date = editForm.value.start_date
      issue.due_date = editForm.value.due_date
      issue.progress = editForm.value.progress
    }

    showEditModal.value = false
  } catch (err) {
    console.error('Failed to update issue:', err)
    alert('更新に失敗しました')
  } finally {
    updating.value = false
  }
}

const goBack = () => {
  router.back()
}

const addIssue = async () => {
  creating.value = true
  createError.value = ''

  try {
    await api.issues.create({
      ...newIssue.value,
      project_id: projectId.value
    })

    // フォームをリセット
    newIssue.value = {
      title: '',
      start_date: '',
      due_date: '',
      assignee_id: null,
      status: '未対応',
      priority: '中',
      progress: 0
    }

    // タスクリストを更新
    await fetchIssues()

    // 今日の位置にスクロール
    scrollToToday()
  } catch (err) {
    console.error('Failed to add issue:', err)
    createError.value = err.response?.data?.detail || 'タスクの追加に失敗しました'
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.sticky {
  position: sticky;
}
</style>
