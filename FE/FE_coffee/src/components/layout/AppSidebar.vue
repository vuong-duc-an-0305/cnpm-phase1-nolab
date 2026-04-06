<template>
  <aside
    :class="[
      'fixed left-0 top-0 z-40 h-screen transition-transform duration-300 ease-in-out',
      'bg-gradient-to-b from-coffee-700 to-coffee-800 w-64 shadow-2xl',
      isOpen ? 'translate-x-0' : '-translate-x-full',
    ]"
  >
    <div class="flex h-full flex-col">
      <!-- Logo Section -->
      <div class="flex items-center gap-3 p-6 border-b border-coffee-600">
        <div class="bg-gradient-to-br from-coffee-500 to-coffee-300 p-2 rounded-xl">
          <Coffee class="w-8 h-8 text-white" />
        </div>
        <div>
          <h1 class="text-xl font-bold text-white">Xưởng Coffee</h1>
          <p class="text-xs text-coffee-300">Management System</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto p-4 space-y-2">
        <router-link
          v-for="item in menuItems"
          :key="item.id"
          :to="item.route"
          :class="[
            'w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
            'hover:bg-coffee-600/50 hover:text-white',
            isActiveRoute(item.route)
              ? 'bg-gradient-to-r from-coffee-500 to-coffee-400 text-white shadow-lg scale-105'
              : 'text-coffee-300',
          ]"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span class="font-medium">{{ item.label }}</span>
          <span
            v-if="item.badge"
            class="ml-auto bg-red-500 text-white text-xs px-2 py-1 rounded-full"
          >
            {{ item.badge }}
          </span>
        </router-link>
      </nav>

      <!-- User Section -->
      <div class="p-4 border-t border-coffee-600">
        <div class="flex items-center gap-3 p-3 bg-coffee-600/50 rounded-xl">
          <div
            class="w-10 h-10 rounded-full bg-gradient-to-br from-coffee-500 to-coffee-400 flex items-center justify-center text-white font-bold"
          >
            {{ userInitials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-semibold text-white truncate">{{ authUser.name }}</p>
            <p class="text-xs text-coffee-300 truncate">
              {{ authUser.role === 'admin' ? 'Administrator' : 'Thu ngân' }}
            </p>
          </div>
          <button
            @click="toggleUserMenu"
            class="text-coffee-300 hover:text-white transition-colors"
          >
            <ChevronDown class="w-4 h-4" />
          </button>
        </div>

        <!-- User Dropdown Menu -->
        <div
          v-if="showUserMenu"
          class="absolute bottom-16 left-4 right-4 bg-white rounded-xl shadow-lg border border-coffee-200 py-2 z-50"
        >
          <button
            @click="handleProfile"
            class="w-full px-4 py-2 text-left text-sm text-coffee-700 hover:bg-coffee-50 transition-colors"
          >
            <User class="w-4 h-4 inline mr-2" />
            Thông tin cá nhân
          </button>
          <button
            @click="handleSettings"
            class="w-full px-4 py-2 text-left text-sm text-coffee-700 hover:bg-coffee-50 transition-colors"
          >
            <Settings class="w-4 h-4 inline mr-2" />
            Cài đặt
          </button>
          <hr class="my-2 border-coffee-200" />
          <button
            @click="handleLogout"
            class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut class="w-4 h-4 inline mr-2" />
            Đăng xuất
          </button>
        </div>
      </div>
    </div>
  </aside>

  <!-- Overlay for mobile -->
  <div
    v-if="isOpen"
    @click="closeSidebar"
    class="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
  />
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Coffee,
  Activity,
  ShoppingCart,
  Package,
  Users,
  Warehouse,
  UserCheck,
  TrendingUp,
  ChevronDown,
  User,
  Settings,
  LogOut,
} from 'lucide-vue-next'
import type { User as UserType } from '../../types'
import { useAuth } from '../../composables/useAuth'

interface MenuItem {
  id: string
  label: string
  route: string
  icon: any
  badge?: string | number
}

interface Props {
  isOpen: boolean
  user?: UserType | null
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false,
  user: null,
})

const emit = defineEmits<{
  close: []
  profile: []
  settings: []
  logout: []
}>()

const route = useRoute()
const router = useRouter()
const showUserMenu = ref(false)
const { menuItems: authMenuItems, user: authUser } = useAuth()

// Sử dụng menu items từ auth composable
const menuItems = computed(() => {
  return authMenuItems.value.map((item) => ({
    id: item.name,
    label: item.label,
    route: item.path,
    icon: getIconComponent(item.icon),
    // badge: có thể gán động từ store sau này; bỏ hard-code
    badge: undefined,
  }))
})

// Helper function để get icon component
const getIconComponent = (iconName: string) => {
  const iconMap: Record<string, any> = {
    BarChart3: Activity,
    ShoppingCart: ShoppingCart,
    Package: Package,
    Users: Users,
    UserCheck: UserCheck,
    Warehouse: Warehouse,
    FileText: TrendingUp,
  }
  return iconMap[iconName] || Activity
}

const userInitials = computed(() => {
  if (authUser.value.name) {
    return authUser.value.name.charAt(0).toUpperCase()
  }
  return 'A'
})

const isActiveRoute = (routePath: string): boolean => {
  return route.path === routePath || route.path.startsWith(routePath + '/')
}

const closeSidebar = () => {
  emit('close')
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
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
  if (!target.closest('.user-menu')) {
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
