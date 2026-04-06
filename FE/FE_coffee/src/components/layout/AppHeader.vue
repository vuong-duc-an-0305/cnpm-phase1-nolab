<template>
  <header class="bg-white border-b border-coffee-200 sticky top-0 z-30 shadow-sm">
    <div class="flex items-center justify-between px-6 py-4">
      <!-- Left Section -->
      <div class="flex items-center gap-4">
        <!-- Mobile Menu Button -->
        <button
          @click="$emit('toggleSidebar')"
          class="p-2 hover:bg-coffee-100 rounded-lg transition-colors lg:hidden"
        >
          <Menu class="w-6 h-6 text-coffee-600" />
        </button>

        <!-- Desktop Menu Button -->
        <button
          @click="$emit('toggleSidebar')"
          class="hidden lg:block p-2 hover:bg-coffee-100 rounded-lg transition-colors"
        >
          <Menu class="w-6 h-6 text-coffee-600" />
        </button>
      </div>

      <!-- Right Section -->
      <div class="flex items-center gap-4">
        <!-- Notifications -->
        <div class="relative dropdown-container">
          <button
            @click="toggleNotifications"
            class="relative p-2 hover:bg-coffee-100 rounded-lg transition-colors"
          >
            <Bell class="w-6 h-6 text-coffee-600" />
            <span v-if="unreadCount > 0" class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          <!-- Notifications Dropdown -->
          <div
            v-if="showNotifications"
            class="dropdown-menu absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-lg border border-coffee-200 z-50"
          >
            <div class="p-4 border-b border-coffee-200">
              <h3 class="font-semibold text-coffee-800">Thông báo</h3>
            </div>
            <div class="max-h-64 overflow-y-auto">
              <div
                v-for="notification in notifications"
                :key="notification.id"
                class="p-4 hover:bg-coffee-50 transition-colors border-b border-coffee-100 last:border-b-0"
              >
                <div class="flex items-start gap-3">
                  <div :class="notificationIconClasses(notification.type)" class="p-2 rounded-lg">
                    <component :is="getNotificationIcon(notification.type)" class="w-4 h-4" />
                  </div>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-coffee-800">{{ notification.title }}</p>
                    <p class="text-xs text-coffee-600 mt-1">{{ notification.message }}</p>
                    <p class="text-xs text-coffee-400 mt-1">{{ formatTime(notification.timestamp) }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="p-4 border-t border-coffee-200">
              <button class="text-sm text-coffee-600 hover:text-coffee-800 transition-colors">
                Xem tất cả thông báo
              </button>
            </div>
          </div>
        </div>

        <!-- User Menu -->
        <div class="relative dropdown-container">
          <button
            @click="toggleUserMenu"
            class="flex items-center gap-3 p-2 hover:bg-coffee-100 rounded-lg transition-colors"
          >
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-coffee-500 to-coffee-400 flex items-center justify-center text-white font-bold text-sm">
              {{ userInitials }}
            </div>
            <div class="hidden md:block text-left">
              <p class="text-sm font-semibold text-coffee-800">{{ user?.firstName }} {{ user?.lastName }}</p>
              <p class="text-xs text-coffee-600">{{ user?.role }}</p>
            </div>
            <ChevronDown class="w-4 h-4 text-coffee-600" />
          </button>

          <!-- User Dropdown -->
          <div
            v-if="showUserMenu"
            class="dropdown-menu absolute right-0 top-full mt-2 w-48 bg-white rounded-xl shadow-lg border border-coffee-200 z-50"
          >
            <div class="py-2">
              <button
                @click="handleProfile"
                class="w-full px-4 py-2 text-left text-sm text-coffee-700 hover:bg-coffee-50 transition-colors flex items-center gap-2"
              >
                <User class="w-4 h-4" />
                Thông tin cá nhân
              </button>
              <button
                @click="handleSettings"
                class="w-full px-4 py-2 text-left text-sm text-coffee-700 hover:bg-coffee-50 transition-colors flex items-center gap-2"
              >
                <Settings class="w-4 h-4" />
                Cài đặt
              </button>
              <hr class="my-2 border-coffee-200">
              <button
                @click="handleLogout"
                class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center gap-2"
              >
                <LogOut class="w-4 h-4" />
                Đăng xuất
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import {
  Menu,
  Bell,
  ChevronDown,
  User,
  Settings,
  LogOut,
  AlertCircle,
  CheckCircle,
  Info,
  AlertTriangle
} from 'lucide-vue-next'
import type { User as UserType, Notification } from '@/types'

interface Props {
  user?: UserType | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleSidebar: []
  profile: []
  settings: []
  logout: []
}>()

// Define local Notification interface with timestamp
interface NotificationItem {
  id: string
  type: string
  title: string
  message: string
  timestamp: Date
}

const showNotifications = ref(false)
const showUserMenu = ref(false)

const notifications = ref<NotificationItem[]>([])

const unreadCount = computed(() => notifications.value.length)

const userInitials = computed(() => {
  if (!props.user) return 'A'
  const firstName = props.user.firstName || ''
  const lastName = props.user.lastName || ''
  return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() || 'A'
})

const getNotificationIcon = (type: string) => {
  const iconMap = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info
  }
  return iconMap[type as keyof typeof iconMap] || Info
}

const notificationIconClasses = (type: string) => {
  const classMap = {
    success: 'bg-green-100 text-green-600',
    error: 'bg-red-100 text-red-600',
    warning: 'bg-yellow-100 text-yellow-600',
    info: 'bg-blue-100 text-blue-600'
  }
  return classMap[type as keyof typeof classMap] || 'bg-coffee-100 text-coffee-600'
}

const formatTime = (timestamp: Date): string => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return 'Vừa xong'
  if (minutes < 60) return `${minutes} phút trước`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} giờ trước`
  
  const days = Math.floor(hours / 24)
  return `${days} ngày trước`
}

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showNotifications.value = false
}

const handleProfile = () => {
  showUserMenu.value = false
  emit('profile')
}

const handleSettings = () => {
  showUserMenu.value = false
  emit('settings')
}

const handleLogout = () => {
  showUserMenu.value = false
  emit('logout')
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  // Kiểm tra xem click có nằm trong dropdown container không
  if (!target.closest('.dropdown-container')) {
    showNotifications.value = false
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
