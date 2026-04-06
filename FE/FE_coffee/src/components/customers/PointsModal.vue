<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-coffee-200">
        <h3 class="text-lg font-semibold text-coffee-800">Quản lý điểm thành viên</h3>
        <button
          @click="$emit('close')"
          class="text-coffee-400 hover:text-coffee-600 transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Customer Info -->
      <div v-if="customer" class="px-6 py-4 bg-coffee-50 border-b border-coffee-200">
        <div class="text-center">
          <h4 class="font-medium text-coffee-800">{{ customer.FullName }}</h4>
          <p class="text-sm text-coffee-500">{{ customer.PhoneNumber }}</p>
          <div class="mt-2">
            <span class="text-lg font-bold text-coffee-800">{{ customer.LoyaltyPoints }} điểm</span>
            <span :class="getMembershipClasses(customer.membership_level)" class="ml-2 px-2 py-1 text-xs rounded-lg font-medium">
              {{ getMembershipText(customer.membership_level) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Action Tabs -->
      <div class="flex border-b border-coffee-200">
        <button
          @click="activeTab = 'add'"
          :class="[
            'flex-1 px-4 py-3 text-sm font-medium transition-colors',
            activeTab === 'add'
              ? 'text-coffee-600 border-b-2 border-coffee-500 bg-coffee-50'
              : 'text-coffee-500 hover:text-coffee-600'
          ]"
        >
          <Plus class="w-4 h-4 inline mr-2" />
          Thêm điểm
        </button>
        <button
          @click="activeTab = 'redeem'"
          :class="[
            'flex-1 px-4 py-3 text-sm font-medium transition-colors',
            activeTab === 'redeem'
              ? 'text-coffee-600 border-b-2 border-coffee-500 bg-coffee-50'
              : 'text-coffee-500 hover:text-coffee-600'
          ]"
        >
          <Minus class="w-4 h-4 inline mr-2" />
          Đổi điểm
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Points Input -->
        <div>
          <label for="points" class="block text-sm font-medium text-coffee-700 mb-1">
            Số điểm <span class="text-red-500">*</span>
          </label>
          <input
            id="points"
            v-model.number="form.points"
            type="number"
            min="1"
            required
            class="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.points }"
            :placeholder="activeTab === 'add' ? 'Nhập số điểm cần thêm' : 'Nhập số điểm cần đổi'"
          />
          <p v-if="errors.points" class="text-red-500 text-xs mt-1">{{ errors.points[0] }}</p>
        </div>

        <!-- Note -->
        <div>
          <label for="note" class="block text-sm font-medium text-coffee-700 mb-1">
            Ghi chú
          </label>
          <textarea
            id="note"
            v-model="form.note"
            rows="3"
            class="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
            :placeholder="activeTab === 'add' ? 'Lý do thêm điểm (tùy chọn)' : 'Lý do đổi điểm (tùy chọn)'"
          ></textarea>
        </div>

        <!-- Preview -->
        <div v-if="form.points > 0" class="bg-coffee-50 rounded-lg p-4">
          <div class="text-sm text-coffee-600 mb-2">
            {{ activeTab === 'add' ? 'Sau khi thêm:' : 'Sau khi đổi:' }}
          </div>
          <div class="flex items-center justify-between">
            <span class="font-medium text-coffee-800">Điểm hiện tại:</span>
            <span class="text-coffee-600">{{ customer?.LoyaltyPoints || 0 }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="font-medium text-coffee-800">
              {{ activeTab === 'add' ? 'Điểm thêm:' : 'Điểm đổi:' }}
            </span>
            <span :class="activeTab === 'add' ? 'text-green-600' : 'text-red-600'">
              {{ activeTab === 'add' ? '+' : '-' }}{{ form.points }}
            </span>
          </div>
          <div class="flex items-center justify-between border-t border-coffee-200 pt-2 mt-2">
            <span class="font-bold text-coffee-800">Điểm mới:</span>
            <span class="font-bold text-coffee-800">
              {{ getNewPoints() }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 pt-4">
          <BaseButton
            type="button"
            variant="secondary"
            @click="$emit('close')"
            class="flex-1"
            :disabled="loading"
          >
            Hủy
          </BaseButton>
          <BaseButton
            type="submit"
            :variant="activeTab === 'add' ? 'primary' : 'danger'"
            class="flex-1"
            :disabled="loading || form.points <= 0"
          >
            <Loader2 v-if="loading" class="w-4 h-4 mr-2 animate-spin" />
            {{ activeTab === 'add' ? 'Thêm điểm' : 'Đổi điểm' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { X, Plus, Minus, Loader2 } from 'lucide-vue-next'
import BaseButton from '@/components/common/BaseButton.vue'
import { customerService } from '@/services/customers'
import type { Customer, CustomerPointsForm } from '@/types'

interface Props {
  customer?: Customer | null
}

interface Emits {
  (e: 'close'): void
  (e: 'saved'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const toast = useToast()

// State
const activeTab = ref<'add' | 'redeem'>('add')
const loading = ref(false)
const errors = ref<Record<string, string[]>>({})

const form = ref<CustomerPointsForm>({
  points: 0,
  note: ''
})

// Computed
const getNewPoints = (): number => {
  if (!props.customer || !form.value.points) return props.customer?.LoyaltyPoints || 0
  
  const currentPoints = props.customer.LoyaltyPoints || 0
  return activeTab.value === 'add' 
    ? currentPoints + form.value.points
    : Math.max(0, currentPoints - form.value.points)
}

// Methods
const getMembershipClasses = (level?: string): string => {
  const classMap = {
    'VIP': 'bg-purple-100 text-purple-700',
    'Gold': 'bg-yellow-100 text-yellow-700',
    'Silver': 'bg-gray-100 text-gray-700',
    'Bronze': 'bg-orange-100 text-orange-700'
  }
  return classMap[level as keyof typeof classMap] || 'bg-coffee-100 text-coffee-700'
}

const getMembershipText = (level?: string): string => {
  return level || 'Thường'
}

const validateForm = (): boolean => {
  errors.value = {}
  let isValid = true

  if (!form.value.points || form.value.points <= 0) {
    errors.value.points = ['Số điểm phải lớn hơn 0']
    isValid = false
  }

  if (activeTab.value === 'redeem' && props.customer) {
    const currentPoints = props.customer.LoyaltyPoints || 0
    if (form.value.points > currentPoints) {
      errors.value.points = ['Không đủ điểm để đổi']
      isValid = false
    }
  }

  return isValid
}

const handleSubmit = async () => {
  if (!props.customer || !validateForm()) {
    return
  }

  try {
    loading.value = true
    errors.value = {}

    if (activeTab.value === 'add') {
      await customerService.addPoints(props.customer.CustomerID, form.value.points, form.value.note)
      toast.success(`Đã thêm ${form.value.points} điểm cho khách hàng`)
    } else {
      await customerService.redeemPoints(props.customer.CustomerID, form.value.points, form.value.note)
      toast.success(`Đã đổi ${form.value.points} điểm của khách hàng`)
    }

    emit('saved')
  } catch (error: any) {
    console.error('Error managing points:', error)
    
    if (error.response?.data) {
      const errorData = error.response.data
      
      if (errorData.points) {
        errors.value.points = errorData.points
        return
      }
      
      if (errorData.error) {
        toast.error(errorData.error)
        return
      }
    }
    
    toast.error('Có lỗi xảy ra khi quản lý điểm')
  } finally {
    loading.value = false
  }
}
</script>
