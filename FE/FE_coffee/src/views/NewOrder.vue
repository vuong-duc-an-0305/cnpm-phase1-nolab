<template>
  <div class="space-y-6">
    <div class="card p-6">
      <h3 class="text-lg font-bold text-coffee-800 mb-4">Tạo đơn hàng mới</h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Số điện thoại khách hàng (tùy chọn)</label>
          <div class="flex gap-2">
            <div class="relative flex-1">
              <input 
                v-model="customerPhone" 
                type="tel" 
                class="input-field w-full" 
                placeholder="Nhập SĐT (VD: 0901234567)" 
                @input="onPhoneInput"
              />
              <div v-if="searchingCustomer" class="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-coffee-600"></div>
              </div>
            </div>
            <button 
              v-if="customerPhone && !foundCustomer"
              @click="searchCustomerByPhone"
              :disabled="searchingCustomer"
              class="btn-secondary px-3"
            >
              <span v-if="searchingCustomer">...</span>
              <span v-else>Tìm</span>
            </button>
          </div>
          <!-- Hiển thị thông tin khách hàng đã tìm thấy -->
          <div v-if="foundCustomer" class="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div class="text-sm text-green-800">
              <div class="font-semibold">{{ foundCustomer.FullName }}</div>
              <div>SĐT: {{ foundCustomer.PhoneNumber }}</div>
              <div v-if="foundCustomer.Email">Email: {{ foundCustomer.Email }}</div>
              <div>Điểm tích lũy: {{ foundCustomer.LoyaltyPoints }}</div>
            </div>
            <button 
              @click="clearCustomer"
              class="text-xs text-red-600 mt-1 hover:text-red-800"
            >
              Xóa
            </button>
          </div>
          <!-- Hiển thị lỗi không tìm thấy -->
          <div v-if="customerPhone && !foundCustomer && !searchingCustomer && phoneError" class="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
            {{ phoneError }}
          </div>
        </div>
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Tên nhân viên</label>
          <input v-model="orderForm.EmployeeName" type="text" class="input-field" placeholder="Tự động điền từ tài khoản" readonly />
        </div>
        <div>
          <label class="block text-sm text-coffee-600 mb-1">Phương thức thanh toán</label>
          <select v-model="orderForm.PaymentMethod" class="input-field">
            <option value="CASH">Tiền mặt</option>
            <option value="CARD">Thẻ</option>
            <option value="MOMO">MoMo</option>
            <option value="BANKING">Chuyển khoản</option>
          </select>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card p-4">
          <h4 class="font-semibold text-coffee-800 mb-3">Chọn sản phẩm</h4>
          <div class="flex gap-2 mb-3">
            <input v-model="productSearch" class="input-field" placeholder="Tìm sản phẩm (tự động tải từ API)" @input="debouncedLoadProducts" />
            <button class="btn-secondary" @click="() => loadProducts()">Tải lại</button>
          </div>
          <div class="max-h-80 overflow-auto space-y-2">
            <div v-for="p in filteredProducts" :key="p.ProductID" class="flex items-center justify-between p-3 bg-coffee-50 rounded-xl">
              <div>
                <div class="font-semibold text-coffee-800">{{ p.ProductName }}</div>
                <div class="text-sm text-coffee-600">{{ formatCurrency(p.Price) }}</div>
              </div>
              <button class="btn-primary" @click="addItem(p)">Thêm</button>
            </div>
          </div>
        </div>

        <div class="card p-4">
          <h4 class="font-semibold text-coffee-800 mb-3">Giỏ hàng</h4>
          <div v-if="orderForm.items.length === 0" class="text-coffee-600">Chưa có sản phẩm</div>
          <div v-else class="space-y-3">
            <div v-for="(it, idx) in orderForm.items" :key="idx" class="p-3 bg-coffee-50 rounded-xl">
              <div class="flex items-center justify-between gap-2">
                <div class="font-semibold text-coffee-800">{{ it.ProductName }}</div>
                <div class="text-coffee-800 font-semibold">{{ formatCurrency(it.UnitPrice) }}</div>
              </div>
              <div class="mt-2 grid grid-cols-3 gap-2">
                <input type="number" min="1" class="input-field" v-model.number="it.Quantity" @focus="it._prevQuantity = it.Quantity" @change="onQuantityChange(it, idx)" />
                <input class="input-field col-span-2" placeholder="Ghi chú" v-model="it.ToppingNote" />
              </div>
              <div class="flex justify-between items-center mt-2">
                <span class="text-sm text-coffee-600">Tạm tính</span>
                <span class="font-semibold">{{ formatCurrency(it.Quantity * it.UnitPrice) }}</span>
              </div>
              <div class="text-right mt-2">
                <button class="text-red-600" @click="removeItem(idx)">Xóa</button>
              </div>
            </div>
          </div>
          <div class="border-t border-coffee-200 mt-4 pt-4 space-y-2">
            <div class="flex justify-between"><span>Tổng</span><span class="font-semibold">{{ formatCurrency(totalAmount) }}</span></div>
            <div class="flex justify-between"><span>Giảm giá</span><input type="number" min="0" class="input-field w-32" v-model.number="orderForm.Discount" /></div>
            <div class="flex justify-between"><span>Thành tiền</span><span class="font-bold">{{ formatCurrency(finalAmount) }}</span></div>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-3 mt-4">
        <button class="btn-secondary" @click="$router.push('/orders')">Hủy</button>
        <button class="btn-primary" :disabled="submitting || orderForm.items.length===0" @click="submitOrder">
          {{ submitting ? 'Đang tạo...' : 'Tạo đơn' }}
        </button>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useRoute, useRouter } from 'vue-router'
import { productService } from '../services/products'
import { customerService } from '../services/customers'
import { orderService } from '../services/orders'
import { apiService } from '../services/api'
import { productService as prodSvc } from '../services/products'

interface CartItem {
  ProductID: number
  ProductName: string
  UnitPrice: number
  Quantity: number
  ToppingNote?: string
  _prevQuantity?: number
}

const emit = defineEmits<{
  (e: 'created', order: any): void
}>()

const route = useRoute()
const router = useRouter()
const toast = useToast()

const products = ref<Array<{ProductID:number; ProductName:string; Price:string}>>([])
const loadingProducts = ref(false)
const productSearch = ref('')

// Customer phone search
const customerPhone = ref('')
const foundCustomer = ref<any>(null)
const searchingCustomer = ref(false)
const phoneError = ref('')
let phoneSearchTimer: ReturnType<typeof setTimeout> | null = null

const orderForm = ref({
  CustomerID: undefined as number | undefined,
  EmployeeID: 1 as any,
  EmployeeName: '',
  PaymentMethod: 'CASH',
  Discount: 0,
  items: [] as CartItem[]
})

const filteredProducts = computed(() => {
  const q = productSearch.value.trim().toLowerCase()
  if (!q) return products.value
  return products.value.filter(p => p.ProductName.toLowerCase().includes(q))
})

const totalAmount = computed(() => orderForm.value.items.reduce((s, it) => s + it.UnitPrice * it.Quantity, 0))
const finalAmount = computed(() => Math.max(0, totalAmount.value - (orderForm.value.Discount || 0)))

function formatCurrency(value: string | number) {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(Number(value))
}

// Customer phone search methods
function onPhoneInput() {
  // Clear previous results when user types
  foundCustomer.value = null
  phoneError.value = ''
  
  // Debounce search
  if (phoneSearchTimer) {
    clearTimeout(phoneSearchTimer)
    phoneSearchTimer = null
  }
  
  const phone = customerPhone.value.trim()
  if (phone && /^(0|\+84)[0-9]{9,10}$/.test(phone)) {
    phoneSearchTimer = setTimeout(() => {
      searchCustomerByPhone()
      phoneSearchTimer = null
    }, 800) // Search after 800ms of no typing
  }
}

async function searchCustomerByPhone() {
  if (!customerPhone.value.trim()) {
    foundCustomer.value = null
    phoneError.value = ''
    return
  }

  // Tránh gọi API nếu đang search
  if (searchingCustomer.value) {
    return
  }

  // Validate phone format
  const phone = customerPhone.value.trim()
  if (!/^(0|\+84)[0-9]{9,10}$/.test(phone)) {
    phoneError.value = 'SĐT không đúng định dạng (VD: 0901234567 hoặc +84901234567)'
    foundCustomer.value = null
    return
  }

  try {
    searchingCustomer.value = true
    phoneError.value = ''
    
    const response = await apiService.get(`/customers/by_phone/?phone=${encodeURIComponent(phone)}`)
    
    // Kiểm tra response có hợp lệ không
    if (response && typeof response === 'object' && response.CustomerID) {
      // Chỉ hiển thị toast nếu chưa có khách hàng hoặc khách hàng khác
      if (!foundCustomer.value || foundCustomer.value.CustomerID !== response.CustomerID) {
        foundCustomer.value = response
        orderForm.value.CustomerID = response.CustomerID
        toast.success(`Đã tìm thấy khách hàng: ${response.FullName}`)
      } else {
        foundCustomer.value = response
        orderForm.value.CustomerID = response.CustomerID
      }
    } else {
      // Response không hợp lệ hoặc rỗng
      phoneError.value = 'Không tìm thấy khách hàng với SĐT này'
      foundCustomer.value = null
      orderForm.value.CustomerID = undefined
    }
  } catch (error: any) {
    console.error('Search customer by phone error:', error)
    
    // Xử lý lỗi dựa trên status code
    if (error?.response?.status === 404) {
      phoneError.value = 'Không tìm thấy khách hàng với SĐT này'
      foundCustomer.value = null
      orderForm.value.CustomerID = undefined
    } else if (error?.response?.status === 400) {
      phoneError.value = error?.response?.data?.error || 'Số điện thoại không hợp lệ'
      foundCustomer.value = null
      orderForm.value.CustomerID = undefined
    } else {
      phoneError.value = 'Lỗi khi tìm kiếm khách hàng'
      foundCustomer.value = null
      orderForm.value.CustomerID = undefined
    }
  } finally {
    searchingCustomer.value = false
  }
}

function clearCustomer() {
  customerPhone.value = ''
  foundCustomer.value = null
  phoneError.value = ''
  orderForm.value.CustomerID = undefined
}

async function loadProducts(page = 1) {
  try {
    loadingProducts.value = true
    // API hỗ trợ phân trang và các tham số category_id, status, search
    const params: any = {
      status: 1,
      search: productSearch.value || undefined,
      page,
      page_size: 20,
    }
    // Trả về có thể là mảng hoặc object phân trang; chuẩn hoá về mảng dùng results nếu có
    const res: any = await productService.getAll(params)
    const items = Array.isArray(res) ? res : res.results || []
    products.value = items
  } finally {
    loadingProducts.value = false
  }
}

// Không liên kết API cho nhân viên: người dùng tự nhập EmployeeID

let debounceTimer: number | undefined
function debouncedLoadProducts() {
  if (debounceTimer) window.clearTimeout(debounceTimer)
  // @ts-ignore - window.setTimeout returns number in browser
  debounceTimer = window.setTimeout(() => loadProducts(), 400)
}

async function addItem(p: {ProductID:number; ProductName:string; Price:string}) {
  try {
    const check: any = await prodSvc.checkIngredients(p.ProductID, 1)
    if (!check?.is_available) {
      toast.error(`Không đủ nguyên liệu để thêm ${p.ProductName}`)
      return
    }
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.warn('Check ingredients before add failed:', err?.response?.data || err)
  }
  orderForm.value.items.push({
    ProductID: p.ProductID,
    ProductName: p.ProductName,
    UnitPrice: Number(p.Price),
    Quantity: 1,
    ToppingNote: ''
  })
}

function removeItem(idx: number) { orderForm.value.items.splice(idx, 1) }

async function onQuantityChange(it: CartItem, idx: number) {
  const qty = Number(it.Quantity)
  if (!(qty > 0)) { it.Quantity = it._prevQuantity || 1; return }
  try {
    const check: any = await prodSvc.checkIngredients(it.ProductID, qty)
    if (!check?.is_available) {
      toast.error(`Không đủ nguyên liệu cho số lượng ${qty}`)
      it.Quantity = it._prevQuantity || 1
    }
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.warn('Check ingredients failed:', err?.response?.data || err)
  }
}

const submitting = ref(false)
async function submitOrder() {
  submitting.value = true
  try {
    // Validate phone format if provided
    if (customerPhone.value.trim() && !foundCustomer.value) {
      const phone = customerPhone.value.trim()
      if (!/^(0|\+84)[0-9]{9,10}$/.test(phone)) {
        toast.error('SĐT không đúng định dạng')
        submitting.value = false
        return
      }
      toast.error('Vui lòng tìm kiếm khách hàng trước khi tạo đơn hàng')
      submitting.value = false
      return
    }

    const payload = {
      CustomerID: orderForm.value.CustomerID,
      EmployeeID: Number(orderForm.value.EmployeeID) || undefined,
      employee_name: orderForm.value.EmployeeName || undefined,
      PaymentMethod: orderForm.value.PaymentMethod,
      Status: 'PREPARING',
      Discount: Number(orderForm.value.Discount || 0),
      items: orderForm.value.items.map(it => ({
        ProductID: it.ProductID,
        Quantity: it.Quantity,
        ToppingNote: it.ToppingNote || ''
      }))
    }
    const created: any = await apiService.post('/orders/', payload)
    // Nếu BE trả về OrderID, cập nhật trạng thái ngay sang PREPARING
    if (created?.OrderID) {
      try {
        await orderService.updateStatus(created.OrderID, 'PREPARING')
      } catch (err) {
        // eslint-disable-next-line no-console
        console.warn('Update status to PREPARING failed:', err)
      }
    }
    toast.success('Tạo đơn hàng thành công!')
    emit('created', created)
    // Phát sự kiện để các màn hình kho/báo cáo refresh dữ liệu
    try {
      window.dispatchEvent(new CustomEvent('inventory:refresh'))
      window.dispatchEvent(new CustomEvent('reports:refresh'))
    } catch {}
    orderForm.value.items = []
    // Nếu đang ở trang /new-order độc lập, điều hướng về danh sách để thấy bản ghi mới
    if (route.name === 'new-order') {
      router.push('/orders')
    }
  } catch (e:any) {
    // Log chi tiết lỗi ra console để debug
    // e.response?.data có thể bao gồm message, errors (field-level), detail
    // eslint-disable-next-line no-console
    console.error('Create order error:', e)
    // eslint-disable-next-line no-console
    console.error('API response data:', e?.response?.data)
    const data = e?.response?.data || {}
    const baseMsg = data?.error || data?.message || e?.message || 'Vui lòng kiểm tra lại'
    const detailsArr = Array.isArray(data?.details)
      ? data.details
      : (data?.details ? [data.details] : [])
    const details = detailsArr.filter(Boolean).join('; ')
    const finalMsg = details ? `${baseMsg}: ${details}` : baseMsg
    window.alert('Lỗi tạo đơn: ' + finalMsg)
  } finally { submitting.value = false }
}

onMounted(() => { 
  loadProducts()
  
  // Tự động điền tên nhân viên từ thông tin đăng nhập
  const userName = localStorage.getItem('user_name')
  if (userName) {
    orderForm.value.EmployeeName = userName
  }
})

// Cleanup timer khi component unmount
onUnmounted(() => {
  if (phoneSearchTimer) {
    clearTimeout(phoneSearchTimer)
    phoneSearchTimer = null
  }
})
</script>
