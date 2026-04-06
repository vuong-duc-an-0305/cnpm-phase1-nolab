<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-coffee-800">Quản lý kho nguyên liệu</h2>
        <p class="text-coffee-600 mt-1">Tổng cộng {{ filteredIngredients.length }} loại nguyên liệu</p>
      </div>
      <div class="flex gap-2">
        <button class="btn-secondary" @click="openCreate">+ Thêm nguyên liệu</button>
      </div>
    </div>

    <!-- Stats Simple -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Nguyên liệu đã hết</h3><p class="text-2xl font-bold text-red-600">{{ criticalIngredients }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Sắp hết hàng</h3><p class="text-2xl font-bold text-orange-600">{{ lowStockIngredients }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Đủ dùng</h3><p class="text-2xl font-bold text-green-600">{{ sufficientIngredients }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Tổng số nguyên liệu</h3><p class="text-2xl font-bold text-coffee-700">{{ ingredients.length }}</p></div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl p-4 shadow-md">
      <div class="flex items-center gap-3 flex-wrap">
        <input v-model="searchQuery" @input="onSearchInput" class="input-field" placeholder="Tìm nguyên liệu" />
        <select v-model="stockFilter" @change="onFilterChange" class="input-field">
          <option value="all">Tất cả</option>
          <option value="low">Nguyên liệu gần hết</option>
          <option value="critical">Nguyên liệu đã hết</option>
          <option value="sufficient">Đủ dùng</option>
        </select>
        <button class="btn-secondary" @click="fetchIngredients">Lọc</button>
      </div>
    </div>

    <!-- Critical Alerts - Đã hết -->
    <div v-if="criticalIngredients > 0" class="bg-red-50 border-l-4 border-red-500 rounded-xl p-4 flex items-start gap-3 mb-4">
      <AlertTriangle class="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
      <div>
        <h3 class="font-bold text-red-800 mb-2">Nguyên liệu đã hết</h3>
        <div class="text-red-700 text-sm">
          <ul class="space-y-1">
            <li v-for="ing in getCriticalIngredients()" :key="ing.IngredientID" class="flex items-center gap-2">
              <span class="w-2 h-2 bg-red-500 rounded-full"></span>
              {{ ing.IngredientName }} ({{ formatUnit(ing.QuantityInStock, ing.Unit) }} / {{ formatUnit(ing.MinQuantity, ing.Unit) }})
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Low Stock Alerts - Gần hết -->
    <div v-if="lowStockIngredients > 0" class="bg-orange-50 border-l-4 border-orange-500 rounded-xl p-4 flex items-start gap-3 mb-4">
      <AlertTriangle class="w-6 h-6 text-orange-600 flex-shrink-0 mt-1" />
      <div>
        <h3 class="font-bold text-orange-800 mb-2">Nguyên liệu gần hết</h3>
        <div class="text-orange-700 text-sm">
          <ul class="space-y-1">
            <li v-for="ing in getLowStockIngredients()" :key="ing.IngredientID" class="flex items-center gap-2">
              <span class="w-2 h-2 bg-orange-500 rounded-full"></span>
              {{ ing.IngredientName }} ({{ formatUnit(ing.QuantityInStock, ing.Unit) }} / {{ formatUnit(ing.MinQuantity, ing.Unit) }})
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Ingredients Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div
        v-for="ingredient in filteredIngredients"
        :key="ingredient.IngredientID"
        class="card p-6 hover:scale-105 transition-all duration-300"
      >
        
        <!-- Status Badge -->
        <div class="flex justify-end mb-2">
          <span :class="getStatusClasses(ingredient)" class="px-3 py-1 text-xs rounded-lg font-medium">
            {{ getStatusText(ingredient) }}
          </span>
        </div>
        
        <!-- Ingredient Info -->
        <h3 class="text-lg font-bold text-coffee-800 mb-1">
          {{ ingredient.IngredientName }}
          <span v-if="ingredient.Unit" class="text-coffee-600 text-sm font-normal">({{ ingredient.Unit }})</span>
        </h3>
        
        <!-- Stock Info -->
        <div class="space-y-2 mb-4">
          <div class="flex items-center justify-between">
            <span class="text-sm text-coffee-600">Tồn kho:</span>
            <span class="font-bold text-lg text-coffee-800">{{ formatUnit(ingredient.QuantityInStock, ingredient.Unit) }}</span>
          </div>
          
          <!-- Stock Progress Bar -->
          <div class="space-y-1">
            <div class="flex justify-between text-xs text-coffee-600">
              <span>Min: {{ formatUnit(ingredient.MinQuantity, ingredient.Unit) }}</span>
            </div>
            <div class="w-full bg-coffee-200 h-3 rounded-full overflow-hidden">
              <div 
                :class="getProgressColor(ingredient)"
                class="h-full transition-all"
                :style="{ width: `${getStockPercentage(ingredient)}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="flex gap-2">
          <button @click="openAddStock(ingredient)" class="btn-secondary flex-1 inline-flex items-center justify-center text-sm"><Plus class="w-4 h-4 mr-1" />Nhập</button>
          <button @click="openReduceStock(ingredient)" class="btn-ghost flex-1 inline-flex items-center justify-center text-sm">Xuất</button>
          <button @click="openEdit(ingredient)" class="btn-secondary flex-1 inline-flex items-center justify-center text-sm"><Edit class="w-4 h-4 mr-1" />Sửa</button>
          <button @click="confirmDelete(ingredient)" class="btn-danger inline-flex items-center justify-center text-sm"><Trash2 class="w-4 h-4" /></button>
        </div>
      </div>
    </div>

    <!-- Create Ingredient Modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">Thêm nguyên liệu</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm text-coffee-600 mb-1">Tên nguyên liệu</label>
            <input v-model="createForm.IngredientName" class="input-field" placeholder="VD: Sữa tươi" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Đơn vị</label>
            <input v-model="createForm.Unit" class="input-field" placeholder="VD: ml, g, kg..." />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Tồn kho ban đầu</label>
            <input v-model.number="createForm.QuantityInStock" type="number" min="0" step="0.001" class="input-field" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Mức tối thiểu</label>
            <input v-model.number="createForm.MinQuantity" type="number" min="0" step="0.001" class="input-field" />
          </div>
        </div>
        <div v-if="createError" class="text-red-600 text-sm mt-3">{{ createError }}</div>
        <div class="flex justify-end gap-3 mt-4">
          <button class="btn-secondary" :disabled="creating" @click="cancelCreate">Hủy</button>
          <button class="btn-primary" :disabled="creating || !isValidCreate" @click="submitCreate">{{ creating ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>

    <!-- Edit Ingredient Modal -->
    <div v-if="showEdit" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">Sửa nguyên liệu</h3>
        <label class="block text-sm text-coffee-600 mb-1">Tên nguyên liệu</label>
        <input v-model="editForm.IngredientName" class="input-field mb-3" />
        <label class="block text-sm text-coffee-600 mb-1">Đơn vị</label>
        <input v-model="editForm.Unit" class="input-field mb-3" placeholder="VD: ml, g, kg..." />
        <label class="block text-sm text-coffee-600 mb-1">Mức tối thiểu</label>
        <input v-model.number="editForm.MinQuantity" type="number" min="0" step="0.001" class="input-field" />
        <div v-if="editError" class="text-red-600 text-sm mt-3">{{ editError }}</div>
        <div class="flex justify-end gap-3 mt-4">
          <button class="btn-secondary" :disabled="editing" @click="cancelEdit">Hủy</button>
          <button class="btn-primary" :disabled="editing" @click="submitEdit">{{ editing ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-2">Xác nhận xóa</h3>
        <p class="text-coffee-700">Bạn có chắc muốn xóa nguyên liệu <span class="font-semibold">{{ showDeleteConfirm?.IngredientName }}</span>?</p>
        <div class="flex justify-end gap-3 mt-6">
          <button class="btn-secondary" :disabled="deleting" @click="closeDelete">Hủy</button>
          <button class="btn-danger" :disabled="deleting" @click="doDelete">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>

    <!-- Adjust stock modal -->
    <div v-if="showAdjust" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">{{ showAdjust?.mode === 'add' ? 'Nhập kho' : 'Xuất kho' }} - {{ showAdjust?.name }}</h3>
        <label class="block text-sm text-coffee-600 mb-1">Số lượng</label>
        <input v-model.number="adjustForm.quantity" type="number" min="0.001" step="0.001" class="input-field mb-3" />
        <label class="block text-sm text-coffee-600 mb-1">Ghi chú</label>
        <input v-model="adjustForm.note" class="input-field" placeholder="Tuỳ chọn" />
        <div v-if="adjustError" class="text-red-600 text-sm mt-3">{{ adjustError }}</div>
        <div class="flex justify-end gap-3 mt-4">
          <button class="btn-secondary" :disabled="adjusting" @click="cancelAdjust">Hủy</button>
          <button class="btn-primary" :disabled="adjusting" @click="submitAdjust">{{ adjusting ? 'Đang lưu...' : 'Xác nhận' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useToast } from 'vue-toastification'
import {
  Plus,
  AlertTriangle,
  Clock,
  CheckCircle,
  DollarSign,
  Edit,
  Trash2
} from 'lucide-vue-next'
import type { Ingredient } from '../types'
import { inventoryService } from '../services/inventory'

const toast = useToast()
const ingredients = ref<Ingredient[]>([])
const searchQuery = ref('')
const stockFilter = ref('all')
const isLoading = ref(false)

const criticalIngredients = computed(() => 
  ingredients.value.filter(i => Number(i.QuantityInStock) <= 0).length
)

const lowStockIngredients = computed(() => 
  ingredients.value.filter(i => Number(i.QuantityInStock) > 0 && Number(i.QuantityInStock) < Number(i.MinQuantity)).length
)

const sufficientIngredients = computed(() => 
  ingredients.value.filter(i => Number(i.QuantityInStock) >= Number(i.MinQuantity)).length
)


const totalValue = computed(() => ingredients.value.length)

const filteredIngredients = computed(() => {
  let filtered = ingredients.value
  
  if (stockFilter.value === 'critical') {
    filtered = filtered.filter(i => Number(i.QuantityInStock) <= 0)
  } else if (stockFilter.value === 'low') {
    filtered = filtered.filter(i => Number(i.QuantityInStock) > 0 && Number(i.QuantityInStock) < Number(i.MinQuantity))
  } else if (stockFilter.value === 'sufficient') {
    filtered = filtered.filter(i => Number(i.QuantityInStock) >= Number(i.MinQuantity))
  }
  
  return filtered
})

const getStockPercentage = (ingredient: Ingredient): number => {
  if (ingredient.stock_percentage !== undefined && ingredient.stock_percentage !== null) {
    return Math.max(0, Math.min(Number(ingredient.stock_percentage), 100))
  }
  const stock = parseFloat(String(ingredient.QuantityInStock))
  const min = Math.max(1e-9, parseFloat(String(ingredient.MinQuantity)))
  return Math.min((stock / min) * 100, 100)
}

const getStatusClasses = (ingredient: Ingredient): string => {
  const percentage = getStockPercentage(ingredient)
  if (percentage < 30) return 'bg-red-100 text-red-700'
  if (percentage < 70) return 'bg-yellow-100 text-yellow-700'
  return 'bg-green-100 text-green-700'
}

const getStatusText = (ingredient: Ingredient): string => {
  const percentage = getStockPercentage(ingredient)
  if (percentage === 0) return 'Đã hết'
  if (percentage < 30) return 'gần hết'
  if (percentage < 70) return 'Sắp hết'
  return 'Đủ dùng'
}

const getProgressColor = (ingredient: Ingredient): string => {
  const percentage = getStockPercentage(ingredient)
  if (percentage < 30) return 'bg-red-500'
  if (percentage < 70) return 'bg-yellow-500'
  return 'bg-green-500'
}

function formatUnit(value: string | number, unit?: string) {
  const num = Number(value)
  if (isNaN(num)) return `${value} ${unit || ''}`.trim()
  return `${num} ${unit || ''}`.trim()
}

function getCriticalIngredients() {
  return ingredients.value.filter(i => Number(i.QuantityInStock) <= 0)
}

function getLowStockIngredients() {
  return ingredients.value.filter(i => Number(i.QuantityInStock) > 0 && Number(i.QuantityInStock) < Number(i.MinQuantity))
}


async function fetchIngredients() {
  try {
    isLoading.value = true
    const res: any = await inventoryService.getAll({ search: searchQuery.value || undefined, page: 1, page_size: 20 })
    ingredients.value = Array.isArray(res) ? res : (res.results || [])
  } catch (err: any) {
    toast.error('Không tải được danh sách nguyên liệu')
    // eslint-disable-next-line no-console
    console.error('Ingredients fetch error:', err?.response?.data || err)
  } finally { isLoading.value = false }
}

let searchTimer: number | undefined
function onSearchInput() {
  if (searchTimer) window.clearTimeout(searchTimer)
  // @ts-ignore
  searchTimer = window.setTimeout(() => fetchIngredients(), 400)
}

function onFilterChange() {
  // Không cần fetch lại data, chỉ cần filter local data
  // filteredIngredients computed sẽ tự động cập nhật
}

// Create ingredient
const showCreate = ref(false)
const creating = ref(false)
const createError = ref('')
const createForm = ref({ IngredientName: '', Unit: '', QuantityInStock: 0, MinQuantity: 0 })
function openCreate() { showCreate.value = true; createError.value = '' }
function cancelCreate() { showCreate.value = false; createError.value = '' }
const isValidCreate = computed(() => createForm.value.IngredientName.trim().length > 0 && Number(createForm.value.QuantityInStock) >= 0 && Number(createForm.value.MinQuantity) >= 0)
async function submitCreate() {
  if (!isValidCreate.value) return
  try {
    creating.value = true
    createError.value = ''
    await inventoryService.create({
      IngredientName: createForm.value.IngredientName.trim(),
      Unit: (createForm.value.Unit || '').trim() || undefined,
      QuantityInStock: Number(createForm.value.QuantityInStock),
      MinQuantity: Number(createForm.value.MinQuantity),
    })
    showCreate.value = false
    createForm.value = { IngredientName: '', Unit: '', QuantityInStock: 0, MinQuantity: 0 }
    await fetchIngredients()
  } catch (err: any) {
    createError.value = err?.response?.data?.message || err?.response?.data?.detail || 'Không thể tạo nguyên liệu'
    // eslint-disable-next-line no-console
    console.error('Create ingredient error:', err?.response?.data || err)
  } finally { creating.value = false }
}

// Edit ingredient
const showEdit = ref(false)
const editing = ref(false)
const editError = ref('')
const editForm = ref({ IngredientID: 0, IngredientName: '', Unit: '', MinQuantity: 0 })
function openEdit(i: Ingredient) {
  showEdit.value = true
  editError.value = ''
  editForm.value = { IngredientID: i.IngredientID, IngredientName: i.IngredientName, Unit: (i.Unit as any) || '', MinQuantity: Number(i.MinQuantity) }
}
function cancelEdit() { showEdit.value = false; editError.value = '' }
async function submitEdit() {
  try {
    editing.value = true
    editError.value = ''
    await inventoryService.update(editForm.value.IngredientID, {
      IngredientName: editForm.value.IngredientName.trim(),
      Unit: (editForm.value.Unit || '').trim() || undefined,
      MinQuantity: Number(editForm.value.MinQuantity),
    })
    showEdit.value = false
    await fetchIngredients()
  } catch (err: any) {
    editError.value = err?.response?.data?.message || err?.response?.data?.detail || 'Không thể cập nhật nguyên liệu'
    // eslint-disable-next-line no-console
    console.error('Update ingredient error:', err?.response?.data || err)
  } finally { editing.value = false }
}

// Delete
const showDeleteConfirm = ref<null | Ingredient>(null)
const deleting = ref(false)
function confirmDelete(i: Ingredient) { showDeleteConfirm.value = i }
function closeDelete() { showDeleteConfirm.value = null }
async function doDelete() {
  if (!showDeleteConfirm.value) return
  try {
    deleting.value = true
    const id = showDeleteConfirm.value.IngredientID
    await inventoryService.delete(id)
    // Xóa khỏi danh sách sau khi xóa thành công
    ingredients.value = ingredients.value.filter(x => x.IngredientID !== id)
    closeDelete()
    await fetchIngredients().catch(() => {})
  } catch (err: any) {
    const msg = err?.response?.data?.error || err?.response?.data?.message || err?.response?.data?.detail || 'Không thể xóa nguyên liệu'
    toast.error(msg)
    // eslint-disable-next-line no-console
    console.error('Delete ingredient error:', err?.response?.data || err)
    await fetchIngredients().catch(() => {})
  } finally { deleting.value = false; closeDelete() }
}

// Stock adjust
const showAdjust = ref<null | { mode: 'add' | 'reduce'; id: number; name: string }>(null)
const adjusting = ref(false)
const adjustError = ref('')
const adjustForm = ref({ quantity: 0, note: '' })
function openAddStock(i: Ingredient) { showAdjust.value = { mode: 'add', id: i.IngredientID, name: i.IngredientName }; adjustError.value = ''; adjustForm.value = { quantity: 0, note: '' } }
function openReduceStock(i: Ingredient) { showAdjust.value = { mode: 'reduce', id: i.IngredientID, name: i.IngredientName }; adjustError.value = ''; adjustForm.value = { quantity: 0, note: '' } }
function cancelAdjust() { showAdjust.value = null; adjustError.value = '' }
async function submitAdjust() {
  if (!showAdjust.value) return
  const qty = Number(adjustForm.value.quantity)
  if (!(qty > 0)) { adjustError.value = 'Số lượng phải > 0'; return }
  try {
    adjusting.value = true
    adjustError.value = ''
    if (showAdjust.value.mode === 'add') {
      await inventoryService.addStock(showAdjust.value.id, qty, adjustForm.value.note || undefined)
    } else {
      await inventoryService.reduceStock(showAdjust.value.id, qty, adjustForm.value.note || undefined)
    }
    showAdjust.value = null
    await fetchIngredients()
  } catch (err: any) {
    adjustError.value = err?.response?.data?.message || err?.response?.data?.detail || 'Không thể cập nhật tồn kho'
    // eslint-disable-next-line no-console
    console.error('Adjust stock error:', err?.response?.data || err)
  } finally { adjusting.value = false }
}


onMounted(() => {
  fetchIngredients()
  const handler = () => fetchIngredients()
  window.addEventListener('inventory:refresh', handler)
  ;(window as any).__invRefreshHandler = handler
})

onBeforeUnmount(() => {
  const handler = (window as any).__invRefreshHandler
  if (handler) window.removeEventListener('inventory:refresh', handler)
})

</script>
