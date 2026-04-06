<template>
  <div class="card overflow-hidden">
    <!-- Table Header -->
    <div v-if="title || $slots.header" class="px-6 py-4 border-b border-coffee-200">
      <div class="flex items-center justify-between">
        <h3 v-if="title" class="text-lg font-bold text-coffee-800">{{ title }}</h3>
        <slot name="header" />
      </div>
    </div>

    <!-- Search and Filters -->
    <div v-if="searchable || $slots.filters" class="px-6 py-4 bg-coffee-50 border-b border-coffee-200">
      <div class="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div v-if="searchable" class="relative flex-1 max-w-md">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="searchPlaceholder"
            class="w-full pl-4 pr-4 py-2 bg-white border border-coffee-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
            @input="handleSearch"
          />
        </div>
        <div class="flex gap-2">
          <slot name="filters" />
        </div>
      </div>
    </div>

    <!-- Table Content -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="bg-coffee-50">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              :class="[
                'px-6 py-3 text-left text-xs font-semibold text-coffee-700 uppercase tracking-wider',
                column.align === 'center' ? 'text-center' : '',
                column.align === 'right' ? 'text-right' : '',
                column.width ? `w-${column.width}` : ''
              ]"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <button
                  v-if="column.sortable && sortable"
                  @click="handleSort(column.key)"
                  class="text-coffee-400 hover:text-coffee-600 transition-colors"
                >
                  ↕️
                </button>
              </div>
            </th>
            <th v-if="actions" class="px-6 py-3 text-right text-xs font-semibold text-coffee-700 uppercase tracking-wider">
              Thao tác
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-coffee-200">
          <tr
            v-for="(item, index) in paginatedData"
            :key="getRowKey(item, index)"
            class="hover:bg-coffee-50 transition-colors"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              :class="[
                'px-6 py-4 whitespace-nowrap text-sm',
                column.align === 'center' ? 'text-center' : '',
                column.align === 'right' ? 'text-right' : ''
              ]"
            >
              <slot
                :name="`cell-${column.key}`"
                :item="item"
                :value="getNestedValue(item, column.key)"
                :index="index"
              >
                {{ formatValue(getNestedValue(item, column.key), column.key) }}
              </slot>
            </td>
            <td v-if="actions" class="px-6 py-4 text-right text-sm font-medium">
              <div class="flex justify-end gap-2">
                <slot name="actions" :item="item" :index="index" />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="flex items-center gap-3">
        <div class="spinner"></div>
        <span class="text-coffee-600">{{ loadingText }}</span>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && paginatedData.length === 0" class="flex flex-col items-center justify-center py-12">
      <div class="w-16 h-16 text-coffee-300 mb-4 text-6xl">📦</div>
      <h3 class="text-lg font-semibold text-coffee-600 mb-2">{{ emptyTitle }}</h3>
      <p class="text-coffee-500 text-center max-w-sm">{{ emptyDescription }}</p>
    </div>

    <!-- Pagination -->
    <div v-if="pagination && totalPages > 1" class="px-6 py-4 bg-coffee-50 border-t border-coffee-200 flex items-center justify-between">
      <div class="text-sm text-coffee-600">
        Hiển thị {{ startIndex + 1 }}-{{ endIndex }} trong {{ totalItems }} kết quả
      </div>
      <div class="flex gap-2">
        <button
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
          class="px-3 py-1 bg-white border border-coffee-200 rounded-lg text-sm hover:bg-coffee-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Trước
        </button>
        
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="goToPage(page)"
          :class="[
            'px-3 py-1 rounded-lg text-sm font-medium transition-colors',
            page === currentPage
              ? 'bg-coffee-600 text-white'
              : 'bg-white border border-coffee-200 hover:bg-coffee-50'
          ]"
        >
          {{ page }}
        </button>
        
        <button
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
          class="px-3 py-1 bg-white border border-coffee-200 rounded-lg text-sm hover:bg-coffee-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Sau
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
// Removed icon imports to avoid dependency issues
import type { TableColumn, SortOptions } from '../../types'

interface Props {
  data: any[]
  columns: TableColumn[]
  title?: string
  loading?: boolean
  loadingText?: string
  searchable?: boolean
  searchPlaceholder?: string
  sortable?: boolean
  pagination?: boolean
  pageSize?: number
  actions?: boolean
  // emptyIcon?: any // Removed to simplify
  emptyTitle?: string
  emptyDescription?: string
  rowKey?: string | ((item: any) => string | number)
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  loadingText: 'Đang tải...',
  searchable: false,
  searchPlaceholder: 'Tìm kiếm...',
  sortable: false,
  pagination: false,
  pageSize: 10,
  actions: false,
  // emptyIcon: Package, // Removed
  emptyTitle: 'Không có dữ liệu',
  emptyDescription: 'Không tìm thấy kết quả nào phù hợp với tiêu chí tìm kiếm.',
  rowKey: 'id'
})

const emit = defineEmits<{
  search: [query: string]
  sort: [options: SortOptions]
  pageChange: [page: number]
}>()

const searchQuery = ref('')
const currentPage = ref(1)
const sortField = ref<string>('')
const sortDirection = ref<'asc' | 'desc'>('asc')

const filteredData = computed(() => {
  let result = props.data

  // Search filter
  if (searchQuery.value && props.searchable) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(item => {
      return props.columns.some(column => {
        const value = getNestedValue(item, column.key)
        return String(value).toLowerCase().includes(query)
      })
    })
  }

  // Sort
  if (sortField.value && props.sortable) {
    result = [...result].sort((a, b) => {
      const aValue = getNestedValue(a, sortField.value)
      const bValue = getNestedValue(b, sortField.value)
      
      if (aValue < bValue) return sortDirection.value === 'asc' ? -1 : 1
      if (aValue > bValue) return sortDirection.value === 'asc' ? 1 : -1
      return 0
    })
  }

  return result
})

const paginatedData = computed(() => {
  if (!props.pagination) return filteredData.value

  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return filteredData.value.slice(start, end)
})

const totalItems = computed(() => filteredData.value.length)
const totalPages = computed(() => Math.ceil(totalItems.value / props.pageSize))
const startIndex = computed(() => (currentPage.value - 1) * props.pageSize)
const endIndex = computed(() => Math.min(startIndex.value + props.pageSize, totalItems.value))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const getRowKey = (item: any, index: number): string | number => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(item)
  }
  return item[props.rowKey] || index
}

const getNestedValue = (obj: any, path: string): any => {
  return path.split('.').reduce((current, key) => current?.[key], obj)
}

const formatValue = (value: any, key: string): string => {
  if (value === null || value === undefined) return '-'
  
  // Format currency
  if (key.includes('price') || key.includes('amount') || key.includes('revenue')) {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(value)
  }
  
  // Format date
  if (key.includes('date') || key.includes('Date')) {
    return new Date(value).toLocaleDateString('vi-VN')
  }
  
  // Format number
  if (typeof value === 'number') {
    return value.toLocaleString('vi-VN')
  }
  
  return String(value)
}

const handleSearch = () => {
  currentPage.value = 1
  emit('search', searchQuery.value)
}

const handleSort = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
  
  emit('sort', { field, direction: sortDirection.value })
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    emit('pageChange', page)
  }
}

// Reset pagination when data changes
watch(() => props.data, () => {
  currentPage.value = 1
})
</script>
