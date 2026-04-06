<template>
  <div class="min-h-screen">
    <!-- Sidebar -->
    <AppSidebar
      :is-open="sidebarOpen"
      :user="currentUser"
      @close="closeSidebar"
      @profile="handleProfile"
      @settings="handleSettings"
      @logout="handleLogout"
    />

    <!-- Main Content -->
    <div :class="[
      'transition-all duration-300 ease-in-out',
      sidebarOpen ? 'lg:ml-64' : 'lg:ml-0'
    ]">
      <!-- Header -->
      <AppHeader
        :user="currentUser"
        @toggle-sidebar="toggleSidebar"
        @search="handleSearch"
        @quick-order="handleQuickOrder"
        @profile="handleProfile"
        @settings="handleSettings"
        @logout="handleLogout"
      />

      <!-- Main Content Area -->
      <main class="p-6">
        <router-view v-slot="{ Component }">
          <transition
            name="page"
            mode="out-in"
            appear
          >
            <keep-alive :max="10">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </main>
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="isLoading"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-xl p-6 flex flex-col items-center gap-4">
        <div class="spinner"></div>
        <p class="text-coffee-600 font-medium">{{ loadingMessage }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
// @ts-ignore
import AppSidebar from './AppSidebar.vue'
// @ts-ignore
import AppHeader from './AppHeader.vue'
import type { User } from '../../types'
import { useAuth } from '../../composables/useAuth'
import { authService } from '@/services/api'

const router = useRouter()
const toast = useToast()
const { user: authUser, logout: authLogout, isAuthenticated } = useAuth()

// State
const sidebarOpen = ref(true)
const isLoading = ref(false)
const loadingMessage = ref('Đang tải...')
const profile = ref<User | null>(null)

// User data from auth
const currentUser = computed<User>(() => {
  if (profile.value) {
    return profile.value
  }

  const fallbackRole = (authUser.value.role || 'admin') as User['role']
  const displayName = authUser.value.name || authUser.value.username || fallbackRole

  return {
    id: 0,
    username: authUser.value.username || fallbackRole,
    email: authUser.value.email || '',
    firstName: displayName,
    lastName: '',
    role: fallbackRole,
    isActive: !!authUser.value.token,
  }
})

const loadProfile = async () => {
  if (!isAuthenticated.value) {
    return
  }

  try {
    const data: any = await authService.getProfile()
    if (data) {
      profile.value = {
        id: data.id ?? 0,
        username: data.username ?? '',
        email: data.email ?? '',
        firstName: data.first_name ?? data.full_name ?? data.username ?? '',
        lastName: data.last_name ?? '',
        role: (data.role ?? 'admin') as User['role'],
        isActive: true,
      }

      if (data.role) {
        localStorage.setItem('user_role', data.role)
      }
      if (data.full_name || data.username) {
        localStorage.setItem('user_name', data.full_name || data.username)
      }
      if (data.username) {
        localStorage.setItem('user_username', data.username)
      }
      if (data.email !== undefined) {
        localStorage.setItem('user_email', data.email || '')
      }
    }
  } catch (error) {
    console.error('Không thể tải thông tin người dùng', error)
  }
}

// Methods
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

const handleSearch = (query: string) => {
  // Implement global search functionality
}

const handleQuickOrder = () => {
  router.push('/orders/new')
}

const handleProfile = () => {
  toast.info('Tính năng thông tin cá nhân đang được phát triển')
  // router.push('/profile')
}

const handleSettings = () => {
  toast.info('Tính năng cài đặt đang được phát triển')
  // router.push('/settings')
}

const handleLogout = async () => {
  try {
    isLoading.value = true
    loadingMessage.value = 'Đang đăng xuất...'

    await authService.logout()
    authLogout()
    profile.value = null

    toast.success('Đăng xuất thành công')
    router.push('/login')
  } catch (error) {
    toast.error('Có lỗi xảy ra khi đăng xuất')
  } finally {
    isLoading.value = false
  }
}

// Initialize app
onMounted(() => {
  // Check if user is authenticated
  if (!isAuthenticated.value) {
    // Redirect to login if no token
    router.push('/login')
    return
  }

  loadProfile()
})
</script>

<style scoped>
/* Page transition animations - optimized for performance */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease;
}

.page-enter-from {
  opacity: 0;
}

.page-leave-to {
  opacity: 0;
}

/* Responsive sidebar behavior */
@media (max-width: 1024px) {
  .sidebar-closed {
    transform: translateX(-100%);
  }
}
</style>
