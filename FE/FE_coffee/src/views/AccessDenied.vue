<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="text-center max-w-md">
      <div class="text-8xl mb-6">🚫</div>
      <h1 class="text-4xl font-bold text-coffee-700 mb-4">Không có quyền truy cập</h1>
      <h2 class="text-xl font-semibold text-coffee-600 mb-4">Bạn không có quyền truy cập trang này</h2>
      <p class="text-coffee-500 mb-8">
        Tài khoản <strong>{{ userRole }}</strong> chỉ có thể truy cập trang quản lý đơn hàng.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <BaseButton @click="$router.push('/orders')" variant="primary">
          <ShoppingCart class="w-4 h-4 mr-2" />
          Về trang đơn hàng
        </BaseButton>
        <BaseButton @click="handleLogout" variant="outline">
          <LogOut class="w-4 h-4 mr-2" />
          Đăng xuất
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { ShoppingCart, LogOut } from 'lucide-vue-next'
// @ts-ignore
import BaseButton from '../components/common/BaseButton.vue'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const toast = useToast()
const { user, logout } = useAuth()

const userRole = computed(() => {
  return user.value.role === 'cashier' ? 'Thu ngân' : user.value.role
})

const handleLogout = () => {
  logout()
  toast.success('Đã đăng xuất')
  router.push('/login')
}
</script>










