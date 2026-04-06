<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-bold text-coffee-800">{{ product?.ProductName || 'Chi tiết sản phẩm' }}</h2>
        <p class="text-coffee-600 mt-1">Mã: #{{ product?.ProductID || $route.params.id }}</p>
      </div>
      <BaseButton @click="$router.push('/products')" variant="secondary">
        <ArrowLeft class="w-4 h-4 mr-2" />Quay lại
      </BaseButton>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="card p-6 md:col-span-2">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">Thông tin sản phẩm</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div class="text-sm text-coffee-600">Giá</div>
            <div class="text-xl font-bold text-coffee-800">{{ formatCurrency(product?.Price || 0) }}</div>
          </div>
          <div>
            <div class="text-sm text-coffee-600">Trạng thái</div>
            <span :class="badgeClass" class="px-3 py-1 text-xs rounded-lg font-medium inline-block mt-1">
              {{ product?.status_display || (product?.Status === 1 ? 'Còn hàng' : 'Ngừng kinh doanh') }}
            </span>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <h3 class="text-lg font-bold text-coffee-800 mb-4">Tác vụ</h3>
        <div class="space-y-3">
          <BaseButton class="w-full" variant="primary" @click="$router.push('/new-order')">Tạo đơn hàng</BaseButton>
        </div>
      </div>
    </div>

    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-bold text-coffee-800">Nguyên liệu (định mức/1 sản phẩm)</h3>
        <span v-if="product && product.is_available === false" class="px-3 py-1 text-xs rounded-lg font-medium bg-red-100 text-red-700">Hết hàng</span>
      </div>
      <div v-if="!product?.ingredients || product.ingredients.length === 0" class="text-coffee-600">Sản phẩm chưa có công thức</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead>
            <tr class="text-left text-coffee-600">
              <th class="py-2">Nguyên liệu</th>
              <th class="py-2">Định mức</th>
              <th class="py-2">Tồn hiện tại</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ing in ingredientsList" :key="ing.IngredientID" class="border-t border-coffee-200">
              <td class="py-2 text-coffee-800 font-medium">
                {{ ing.IngredientName }}
                <span v-if="ing.IngredientUnit || ing.Unit" class="text-coffee-600 text-xs font-normal">
                  ({{ ing.IngredientUnit || ing.Unit }})
                </span>
              </td>
              <td class="py-2">{{ formatUnit(ing.Quantity, ing.Unit) }}</td>
              <td class="py-2">{{ formatUnit(ing.QuantityInStock, ing.IngredientUnit || ing.Unit) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import * as BaseButtonModule from '../components/common/BaseButton.vue'
const BaseButton: any = (BaseButtonModule as any).default || BaseButtonModule
import { productService } from '../services/products'
import type { Product } from '../types'

const route = useRoute()
const router = useRouter()
const product = ref<Product | null>(null)
const ingredientsList = computed(() => product.value?.ingredients || [])

function formatCurrency(value: string | number) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(value))
}

function formatUnit(value: string | number, unit: string) {
  const num = Number(value)
  if (isNaN(num)) return `${value} ${unit || ''}`.trim()
  // Hiển thị gọn theo đơn vị, không cố đổi đơn vị
  return `${num} ${unit || ''}`.trim()
}

const badgeClass = computed(() => {
  const st = product?.value?.Status
  if (st === 1) return 'bg-green-100 text-green-700'
  return 'bg-red-100 text-red-700'
})

async function fetchDetail() {
  const id = Number(route.params.id)
  if (!id) return
  product.value = await productService.getById(id)
}

onMounted(() => {
  fetchDetail()
  const invHandler = () => fetchDetail()
  window.addEventListener('inventory:refresh', invHandler)
  ;(window as any).__prodDetailInvHandler = invHandler
})

onBeforeUnmount(() => {
  const invHandler = (window as any).__prodDetailInvHandler
  if (invHandler) window.removeEventListener('inventory:refresh', invHandler)
})
</script>
