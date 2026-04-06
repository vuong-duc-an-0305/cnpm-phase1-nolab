<template>
  <div
    class="min-h-screen bg-gradient-to-br from-coffee-50 to-coffee-100 flex items-center justify-center p-4"
  >
    <div class="max-w-md w-full">
      <!-- Logo and Title -->
      <div class="text-center mb-8">
        <div
          class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-coffee-500 to-coffee-600 rounded-2xl mb-4"
        >
          <Coffee class="w-10 h-10 text-white" />
        </div>
        <h1 class="text-3xl font-bold text-coffee-800 mb-2">Xưởng Coffee</h1>
        <p class="text-coffee-600">Hệ thống quản lý quán cà phê</p>
      </div>

      <!-- Login Form -->
      <div class="card p-8">
        <h2 class="text-2xl font-bold text-coffee-800 mb-6 text-center">Đăng nhập</h2>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <BaseInput
            v-model="form.username"
            label="Tên đăng nhập"
            placeholder="Nhập tên đăng nhập"
            :error="errors.username"
            required
            left-icon="User"
          />

          <BaseInput
            v-model="form.password"
            type="password"
            label="Mật khẩu"
            placeholder="Nhập mật khẩu"
            :error="errors.password"
            required
            left-icon="Lock"
          />

          <div class="flex items-center justify-between">
            <label class="flex items-center">
              <input
                v-model="form.rememberMe"
                type="checkbox"
                class="rounded border-coffee-300 text-coffee-600 focus:ring-coffee-500"
              />
              <span class="ml-2 text-sm text-coffee-600">Ghi nhớ đăng nhập</span>
            </label>
            <a href="#" class="text-sm text-coffee-600 hover:text-coffee-800 transition-colors">
              Quên mật khẩu?
            </a>
          </div>

          <BaseButton
            type="submit"
            :loading="isLoading"
            loading-text="Đang đăng nhập..."
            full-width
            size="lg"
          >
            Đăng nhập
          </BaseButton>
        </form>
      </div>

      <!-- Footer -->
      <div class="text-center mt-8">
        <p class="text-sm text-coffee-500">
          © 2024 Xưởng Coffee Management System. All rights reserved.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { Coffee, User, Lock } from 'lucide-vue-next'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import { authService } from '@/services/api'

const router = useRouter()
const toast = useToast()

const isLoading = ref(false)
const errors = ref<Record<string, string>>({})

const form = reactive({
  username: '',
  password: '',
  rememberMe: false,
})

const handleLogin = async () => {
  try {
    isLoading.value = true
    errors.value = {}
    
    // Basic validation
    if (!form.username) {
      errors.value.username = 'Vui lòng nhập tên đăng nhập'
      return
    }

    if (!form.password) {
      errors.value.password = 'Vui lòng nhập mật khẩu'
      return
    }
    
    const response: any = await authService.login({
      username: form.username,
      password: form.password
    })
    
    // Validate response
    if (!response.token) {
      throw new Error('Không nhận được token từ server')
    }
    
    if (!response.user) {
      throw new Error('Không nhận được thông tin user từ server')
    }
    
    // Store auth data
    localStorage.setItem('auth_token', response.token)
    
    const userData = response.user
    localStorage.setItem('user_role', userData.role || 'admin')
    localStorage.setItem('user_name', userData.full_name || userData.username || 'User')
    localStorage.setItem('user_username', userData.username || '')
    localStorage.setItem('user_email', userData.email || '')
    
    toast.success('Đăng nhập thành công!')
    
    // Redirect based on role
    const userRole = userData.role || 'admin'
    if (userRole === 'cashier') {
      router.push('/orders')
    } else {
      router.push('/dashboard')
    }
    
  } catch (error: any) {
    console.error('❌ Login error:', error)
    if (error.response?.data?.detail) {
      toast.error(error.response.data.detail)
    } else if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else {
      toast.error(error.message || 'Đăng nhập thất bại')
    }
  } finally {
    isLoading.value = false
  }
}

</script>
