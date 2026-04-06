<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-coffee-800">Quản lý sản phẩm</h2>
        <p class="text-coffee-600 mt-1">Tổng cộng {{ products.length }} sản phẩm</p>
      </div>
      <button class="btn-primary inline-flex items-center" @click="openCreate">
        <Plus class="w-4 h-4 mr-2" />
        Thêm sản phẩm
      </button>
    </div>

    <!-- Simple Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Tổng sản phẩm</h3><p class="text-2xl font-bold text-coffee-700">{{ products.length }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Còn hàng</h3><p class="text-2xl font-bold text-coffee-700">{{ inStock }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Hết hàng</h3><p class="text-2xl font-bold text-coffee-700">{{ outOfStock }}</p></div>
      <div class="card p-6"><h3 class="text-coffee-600 text-sm mb-1 font-medium">Ngừng KD</h3><p class="text-2xl font-bold text-coffee-700">{{ discontinued }}</p></div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl p-4 shadow-md">
      <div class="flex items-center gap-3 flex-wrap">
        <input v-model="searchQuery" @input="onSearchInput" class="input-field" placeholder="Tìm tên/ danh mục" />
        <select v-model.number="statusFilter" class="input-field w-40">
          <option :value="undefined">Tất cả trạng thái</option>
          <option :value="1">Còn hàng</option>
          <option :value="0">Hết hàng</option>
          <option :value="2">Ngừng kinh doanh</option>
        </select>
        <select v-model.number="categoryFilter" class="input-field w-56">
          <option :value="undefined">Tất cả danh mục</option>
          <option v-for="c in categories" :key="c.CategoryID" :value="c.CategoryID">{{ c.CategoryName }} ({{ c.product_count || 0 }})</option>
        </select>
        <button class="btn-secondary" @click="fetchProducts">Lọc</button>
        <button class="btn-primary ml-auto" @click="openAddCategory">+ Thêm danh mục</button>
      </div>
    </div>

    <!-- Create Product Inline Form -->
    <div v-if="showCreate" class="card p-6">
      <h3 class="text-lg font-bold text-coffee-800 mb-4">Thêm sản phẩm</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Tên sản phẩm</label>
          <input v-model="createForm.ProductName" class="input-field" placeholder="Nhập tên" />
        </div>
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Giá</label>
          <input v-model.number="createForm.Price" type="number" min="0" class="input-field" placeholder="VD: 30000" />
        </div>
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Ảnh (URL)</label>
          <input v-model="createForm.ImageUrl" class="input-field" placeholder="http://..." />
        </div>
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Danh mục</label>
          <select v-model.number="createForm.CategoryID" class="input-field">
            <option v-for="c in categories" :key="c.CategoryID" :value="c.CategoryID">{{ c.CategoryName }} ({{ c.product_count || 0 }})</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Trạng thái</label>
          <select v-model.number="createForm.Status" class="input-field">
            <option :value="1">Còn hàng</option>
            <option :value="0">Hết hàng</option>
            <option :value="2">Ngừng kinh doanh</option>
          </select>
        </div>
        
        <!-- Ingredients for recipe -->
        <div class="md:col-span-2">
          <label class="block text-sm text-coffee-600 mb-2">Nguyên liệu (định mức cho 1 sản phẩm)</label>
          <div class="space-y-3">
            <div v-for="(ri, idx) in recipeInputs" :key="idx" class="grid grid-cols-12 gap-2 items-center">
              <select v-model.number="ri.IngredientID" @change="onSelectIngredient(idx)" class="input-field col-span-5">
                <option :value="undefined">-- Chọn nguyên liệu --</option>
                <option v-for="i in ingredients" :key="i.IngredientID" :value="i.IngredientID">
                  {{ i.IngredientName }}
                  <span v-if="i.Unit"> ({{ i.Unit }})</span>
                </option>
              </select>
              <input v-model.number="ri.Quantity" type="number" min="0.001" step="0.001" class="input-field col-span-4" placeholder="Số lượng" />
              <span class="col-span-2 input-field inline-flex items-center cursor-default select-none">
                {{ getDefaultUnit(ri.IngredientID) || 'Chọn nguyên liệu' }}
              </span>
              <button class="btn-ghost col-span-1" @click="removeRecipeInput(idx)">Xóa</button>
            </div>
            <button class="btn-secondary" @click="addRecipeInput">+ Thêm nguyên liệu</button>
          </div>
        </div>
      </div>
      <div v-if="createError" class="text-red-600 text-sm mt-3">{{ createError }}</div>
      <div class="flex justify-end gap-3 mt-4">
        <button class="btn-secondary" @click="cancelCreate">Hủy</button>
        <button class="btn-primary" :disabled="creating || !isValidCreate" @click="submitCreate">{{ creating ? 'Đang lưu...' : 'Lưu' }}</button>
      </div>
    </div>

    <!-- Products Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div
        v-for="product in products"
        :key="product.ProductID"
        class="card p-6 hover:scale-105 transition-all duration-300"
      >
        <!-- Product Image -->
        <div class="mb-4 flex items-center justify-center">
          <img
            v-if="hasImage(product)"
            :src="product.ImageUrl"
            :alt="product.ProductName"
            style="width:380px;height:380px"
            class="object-contain rounded-md bg-coffee-50"
            loading="lazy"
            @error="markImgFailed(product.ProductID, $event)"
          />
          <div v-else style="width:380px;height:380px" class="bg-coffee-100 rounded-md flex items-center justify-center text-coffee-400 text-sm">
            Không có ảnh
          </div>
        </div>
        
        <!-- Product Info -->
        <h3 class="text-lg font-bold text-coffee-800 mb-1">{{ product.ProductName }}</h3>
        <p class="text-sm text-coffee-500 mb-3">{{ product.category_name }}</p>
        
        <!-- Price -->
        <div class="flex items-center justify-between mb-4">
          <span class="text-2xl font-bold text-coffee-600">{{ formatCurrency(product.Price) }}</span>
          <span :class="getStatusClasses(product.Status)" class="px-2 py-1 text-xs rounded-lg">
            {{ getStatusText(product.Status) }}
          </span>
        </div>
        
        <!-- Actions -->
        <div class="flex gap-2">
          <button @click="openEdit(product)" class="btn-secondary flex-1 inline-flex items-center justify-center text-sm">
            <Edit class="w-4 h-4 mr-1" />
            Sửa
          </button>
          <button @click="confirmDelete(product)" class="btn-danger inline-flex items-center justify-center text-sm">
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="products.length === 0" class="text-center py-12">
      <Package class="w-16 h-16 text-coffee-300 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-coffee-600 mb-2">Chưa có sản phẩm nào</h3>
      <p class="text-coffee-500 mb-4">Hãy thêm sản phẩm đầu tiên để bắt đầu</p>
      <button class="btn-primary inline-flex items-center" @click="openCreate">
        <Plus class="w-4 h-4 mr-2" />
        Thêm sản phẩm
      </button>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEdit" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-2xl p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">Sửa sản phẩm</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Tên sản phẩm</label>
            <input v-model="editForm.ProductName" class="input-field" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Giá</label>
            <input v-model.number="editForm.Price" type="number" min="0" class="input-field" />
          </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Ảnh (URL)</label>
            <input v-model="editForm.ImageUrl" class="input-field" />
          </div>
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Danh mục</label>
          <select v-model.number="editForm.CategoryID" class="input-field">
            <option v-for="c in categories" :key="c.CategoryID" :value="c.CategoryID">{{ c.CategoryName }} ({{ c.product_count || 0 }})</option>
          </select>
        </div>
          <div>
            <label class="block text-sm text-coffee-600 mb-1">Trạng thái</label>
            <select v-model.number="editForm.Status" class="input-field">
              <option :value="1">Còn hàng</option>
              <option :value="0">Hết hàng</option>
              <option :value="2">Ngừng kinh doanh</option>
            </select>
          </div>
        </div>
        <div v-if="editError" class="text-red-600 text-sm mt-3">{{ editError }}</div>
        
        <!-- Edit Recipes -->
        <div class="mt-6">
          <h4 class="text-md font-bold text-coffee-800 mb-3">Công thức (định mức/1 sản phẩm)</h4>
          <div class="space-y-3">
            <div v-for="(ri, idx) in editRecipeInputs" :key="idx" class="grid grid-cols-12 gap-2 items-center">
              <select v-model.number="ri.IngredientID" @change="onSelectEditIngredient(idx)" class="input-field col-span-5">
                <option :value="undefined">-- Chọn nguyên liệu --</option>
                <option v-for="i in ingredients" :key="i.IngredientID" :value="i.IngredientID">
                  {{ i.IngredientName }}<span v-if="i.Unit"> ({{ i.Unit }})</span>
                </option>
              </select>
              <input v-model.number="ri.Quantity" type="number" min="0.001" step="0.001" class="input-field col-span-4" placeholder="Số lượng" />
              <span class="col-span-2 input-field inline-flex items-center cursor-default select-none">
                {{ getDefaultUnit(ri.IngredientID) || 'Chọn nguyên liệu' }}
              </span>
              <button class="btn-ghost col-span-1" @click="removeEditRecipeInput(idx)">Xóa</button>
            </div>
            <button class="btn-secondary" @click="addEditRecipeInput">+ Thêm nguyên liệu</button>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-4">
          <button class="btn-secondary" @click="cancelEdit">Hủy</button>
          <button class="btn-primary" :disabled="editing" @click="submitEdit">{{ editing ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete confirm -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-2">Xác nhận xóa</h3>
        <p class="text-coffee-700">Bạn có chắc muốn xóa sản phẩm <span class="font-semibold">{{ showDeleteConfirm?.ProductName }}</span>?</p>
        <div class="flex justify-end gap-3 mt-6">
          <button class="btn-secondary" :disabled="deleting" @click="closeDelete">Hủy</button>
          <button class="btn-danger" :disabled="deleting" @click="doDelete">{{ deleting ? 'Đang xóa...' : 'Xóa' }}</button>
        </div>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAddCategory" class="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">Thêm danh mục</h3>
        <label class="block text-sm text-coffee-600 mb-1">Tên danh mục</label>
        <input v-model="newCategoryName" class="input-field" placeholder="VD: Sinh tố" />
        <div v-if="addCategoryError" class="text-red-600 text-sm mt-3">{{ addCategoryError }}</div>
        <div class="flex justify-end gap-3 mt-4">
          <button class="btn-secondary" :disabled="addingCategory" @click="cancelAddCategory">Hủy</button>
          <button class="btn-primary" :disabled="addingCategory" @click="submitAddCategory">{{ addingCategory ? 'Đang lưu...' : 'Lưu' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onActivated } from 'vue'
import { useToast } from 'vue-toastification'
import {
  Plus,
  Package,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Eye,
  Edit,
  Trash2
} from 'lucide-vue-next'
import type { Product } from '../types'
import { productService } from '../services/products'
import { categoryService } from '../services/categories'
import { inventoryService } from '../services/inventory'
import { recipeService } from '../services/recipes'

const toast = useToast()
const products = ref<Product[]>([])
const isInitialized = ref(false)
const searchQuery = ref('')
const statusFilter = ref<number | undefined>(undefined)
const categoryFilter = ref<number | undefined>(undefined)
const categories = ref<Array<{CategoryID:number; CategoryName:string; product_count?: number}>>([])
const showAddCategory = ref(false)
const addingCategory = ref(false)
const addCategoryError = ref('')
const newCategoryName = ref('')

const inStock = computed(() => products.value.filter(p => p.Status === 1).length)
const outOfStock = computed(() => products.value.filter(p => p.Status === 0).length)
const discontinued = computed(() => products.value.filter(p => p.Status === 2).length)
const failedImages = ref<Record<number, boolean>>({})

const formatCurrency = (value: string | number): string => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(Number(value))
}

const getStatusClasses = (status: number): string => {
  const map: Record<number, string> = {
    1: 'bg-green-100 text-green-700',
    0: 'bg-red-100 text-red-700',
    2: 'bg-gray-200 text-gray-700',
  }
  return map[status] || 'bg-coffee-100 text-coffee-700'
}

const getStatusText = (status: number): string => {
  const map: Record<number, string> = {
    1: 'Còn hàng',
    0: 'Hết hàng',
    2: 'Ngừng kinh doanh',
  }
  return map[status] ?? String(status)
}

const isLoading = ref(false)
async function fetchProducts() {
  try {
    isLoading.value = true
    const params: any = {
      search: searchQuery.value || undefined,
      status: statusFilter.value !== undefined ? statusFilter.value : undefined,
      category_id: categoryFilter.value || undefined,
      page: 1,
      page_size: 20,
    }
    const res: any = await productService.getAll(params)
    products.value = Array.isArray(res) ? res : (res.results || [])
    isInitialized.value = true
  } catch (err: any) {
    toast.error('Không tải được danh sách sản phẩm')
    // eslint-disable-next-line no-console
    console.error('Products fetch error:', err?.response?.data || err)
  } finally {
    isLoading.value = false
  }
}

let searchTimer: number | undefined
function onSearchInput() {
  if (searchTimer) window.clearTimeout(searchTimer)
  // @ts-ignore
  searchTimer = window.setTimeout(() => fetchProducts(), 400)
}

function hasImage(p: Product) {
  return !!p.ImageUrl && !failedImages.value[p.ProductID]
}

function markImgFailed(id: number, _e: Event) {
  failedImages.value[id] = true
}

// Create
const showCreate = ref(false)
const creating = ref(false)
const createError = ref('')
const createForm = ref({ ProductName: '', Price: 0, ImageUrl: '', CategoryID: 1, Status: 1 })
const isValidCreate = computed(() => createForm.value.ProductName.trim().length > 0 && Number(createForm.value.Price) > 0 && Number(createForm.value.CategoryID) > 0)
const ingredients = ref<Array<{ IngredientID:number; IngredientName:string; Unit?: string }>>([])
const recipeInputs = ref<Array<{ IngredientID?: number; Quantity: number; Unit: string }>>([])
function addRecipeInput() { recipeInputs.value.push({ IngredientID: undefined, Quantity: 0, Unit: '' }) }
function removeRecipeInput(idx: number) { recipeInputs.value.splice(idx, 1) }
function getDefaultUnit(ingredientId?: number): string | undefined {
  const ing = ingredients.value.find(i => i.IngredientID === ingredientId)
  return (ing?.Unit || undefined) as any
}
function onSelectIngredient(idx: number) {
  const ri = recipeInputs.value[idx]
  if (!ri) return
  const defUnit = getDefaultUnit(ri.IngredientID)
  // Tự động gán đơn vị theo nguyên liệu
  if (defUnit) {
    ri.Unit = defUnit
  }
}
function openCreate() { showCreate.value = true }
function cancelCreate() { showCreate.value = false; createError.value = '' }
async function submitCreate() {
  if (!isValidCreate.value) return
  try {
    creating.value = true
    createError.value = ''
    const created = await productService.create({
      ProductName: createForm.value.ProductName.trim(),
      Price: Number(createForm.value.Price),
      ImageUrl: createForm.value.ImageUrl || undefined,
      CategoryID: Number(createForm.value.CategoryID),
      Status: Number(createForm.value.Status) as any,
    })
    // Create recipes if provided
    const validRecipes = recipeInputs.value
      .filter(r => r.IngredientID && Number(r.Quantity) > 0 && (r.Unit || '').trim().length > 0)
      .map(r => ({ IngredientID: r.IngredientID as number, Quantity: Number(r.Quantity), Unit: r.Unit.trim() }))
    if (created?.ProductID && validRecipes.length > 0) {
      await recipeService.bulkCreate(created.ProductID, validRecipes)
    }
    showCreate.value = false
    createForm.value = { ProductName: '', Price: 0, ImageUrl: '', CategoryID: 1, Status: 1 }
    recipeInputs.value = []
    await fetchProducts()
  } catch (err: any) {
    createError.value = err?.response?.data?.message || err?.response?.data?.detail || 'Không thể tạo sản phẩm'
    // eslint-disable-next-line no-console
    console.error('Create product error:', err?.response?.data || err)
  } finally {
    creating.value = false
  }
}

// Edit
const showEdit = ref(false)
const editing = ref(false)
const editError = ref('')
const editForm = ref({ ProductID: 0, ProductName: '', Price: 0, ImageUrl: '', CategoryID: 1, Status: 1 })
const editRecipeInputs = ref<Array<{ IngredientID?: number; Quantity: number; Unit: string }>>([])
function openEdit(p: Product) {
  showEdit.value = true
  editError.value = ''
  editForm.value = { ProductID: p.ProductID, ProductName: p.ProductName, Price: Number(p.Price), ImageUrl: p.ImageUrl || '', CategoryID: p.CategoryID, Status: p.Status as any }
  // load current recipes
  recipeService.getByProduct(p.ProductID).then((list: any) => {
    editRecipeInputs.value = (list || []).map((r: any) => ({ IngredientID: r.IngredientID, Quantity: Number(r.Quantity), Unit: r.Unit }))
  }).catch(() => { editRecipeInputs.value = [] })
}
function cancelEdit() { showEdit.value = false; editError.value = '' }
async function submitEdit() {
  try {
    editing.value = true
    editError.value = ''
    await productService.update(editForm.value.ProductID, {
      ProductName: editForm.value.ProductName.trim(),
      Price: Number(editForm.value.Price),
      ImageUrl: editForm.value.ImageUrl || undefined,
      CategoryID: Number(editForm.value.CategoryID),
      Status: Number(editForm.value.Status) as any,
    })
    // update recipes: delete old and bulk create new if any
    try {
      await recipeService.deleteByProduct(editForm.value.ProductID)
    } catch (_) { /* ignore */ }
    const validEdits = editRecipeInputs.value
      .filter(r => r.IngredientID && Number(r.Quantity) > 0 && (r.Unit || '').trim().length > 0)
      .map(r => ({ IngredientID: r.IngredientID as number, Quantity: Number(r.Quantity), Unit: r.Unit.trim() }))
    if (validEdits.length > 0) {
      await recipeService.bulkCreate(editForm.value.ProductID, validEdits)
    }
    showEdit.value = false
    await fetchProducts()
  } catch (err: any) {
    editError.value = err?.response?.data?.message || err?.response?.data?.detail || 'Không thể cập nhật sản phẩm'
    // eslint-disable-next-line no-console
    console.error('Update product error:', err?.response?.data || err)
  } finally {
    editing.value = false
  }
}

function addEditRecipeInput() { editRecipeInputs.value.push({ IngredientID: undefined, Quantity: 0, Unit: '' }) }
function removeEditRecipeInput(idx: number) { editRecipeInputs.value.splice(idx, 1) }
function onSelectEditIngredient(idx: number) {
  const ri = editRecipeInputs.value[idx]
  if (!ri) return
  const defUnit = getDefaultUnit(ri.IngredientID)
  // Tự động gán đơn vị theo nguyên liệu
  if (defUnit) {
    ri.Unit = defUnit
  }
}

// Delete
const showDeleteConfirm = ref<null | Product>(null)
const deleting = ref(false)
function confirmDelete(p: Product) { showDeleteConfirm.value = p }
function closeDelete() { showDeleteConfirm.value = null }
async function doDelete() {
  if (!showDeleteConfirm.value) return
  try {
    deleting.value = true
    const id = showDeleteConfirm.value.ProductID
    closeDelete()
    // optimistic update
    products.value = products.value.filter(x => x.ProductID !== id)
    await productService.delete(id)
    await fetchProducts().catch(() => {})
  } catch (err: any) {
    toast.error(err?.response?.data?.message || err?.response?.data?.detail || 'Không thể xóa sản phẩm')
    // eslint-disable-next-line no-console
    console.error('Delete product error:', err?.response?.data || err)
    await fetchProducts().catch(() => {})
  } finally {
    deleting.value = false
    closeDelete()
  }
}

onMounted(() => { 
  if (!isInitialized.value) {
    fetchProducts() 
  }
})
onMounted(async () => {
  if (!isInitialized.value) {
    try {
      const res: any = await categoryService.getAll()
      categories.value = Array.isArray(res) ? res : (res.results || [])
      // load ingredients for recipe selection
      const ingRes: any = await inventoryService.getAll()
      ingredients.value = Array.isArray(ingRes) ? ingRes : (ingRes.results || [])
    } catch (err) {
      // eslint-disable-next-line no-console
      console.warn('Load categories failed', err)
    }
  }
})

onActivated(() => {
  // Component is reactivated from keep-alive cache
  if (isInitialized.value) {
    isLoading.value = false
  }
})

function openAddCategory() {
  addCategoryError.value = ''
  newCategoryName.value = ''
  showAddCategory.value = true
}

function cancelAddCategory() {
  showAddCategory.value = false
  addCategoryError.value = ''
}

async function submitAddCategory() {
  const name = newCategoryName.value.trim()
  if (!name) {
    addCategoryError.value = 'Tên danh mục không được rỗng'
    return
  }
  // FE validate trùng tên (không phân biệt hoa/thường, bỏ khoảng trắng dư)
  const normalized = name.replace(/\s+/g, ' ').toLowerCase()
  const dup = categories.value.some(c => (c.CategoryName || '').trim().replace(/\s+/g, ' ').toLowerCase() === normalized)
  if (dup) {
    addCategoryError.value = 'Tên danh mục đã tồn tại'
    return
  }
  try {
    addingCategory.value = true
    addCategoryError.value = ''
    const created: any = await categoryService.create({ CategoryName: name })
    // refresh dropdown categories
    const res: any = await categoryService.getAll()
    categories.value = Array.isArray(res) ? res : (res.results || [])
    // chọn luôn danh mục vừa thêm để lọc
    if (created?.CategoryID) {
      categoryFilter.value = created.CategoryID
      await fetchProducts()
    }
    showAddCategory.value = false
  } catch (err: any) {
    addCategoryError.value = err?.response?.data?.CategoryName?.[0] || err?.response?.data?.message || err?.message || 'Không thể tạo danh mục'
    // eslint-disable-next-line no-console
    console.error('Create category error:', err?.response?.data || err)
  } finally {
    addingCategory.value = false
  }
}
</script>
