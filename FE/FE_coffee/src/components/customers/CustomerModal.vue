<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-coffee-200">
        <h3 class="text-lg font-semibold text-coffee-800">
          {{ isEditing ? 'Chỉnh sửa khách hàng' : 'Thêm khách hàng mới' }}
        </h3>
        <button
          @click="$emit('close')"
          class="text-coffee-400 hover:text-coffee-600 transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Full Name -->
        <div>
          <label for="fullName" class="block text-sm font-medium text-coffee-700 mb-1">
            Họ và tên <span class="text-red-500">*</span>
          </label>
          <input
            id="fullName"
            v-model="form.FullName"
            type="text"
            required
            class="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.FullName }"
            placeholder="Nhập họ và tên"
          />
          <p v-if="errors.FullName" class="text-red-500 text-xs mt-1">{{ errors.FullName[0] }}</p>
        </div>

        <!-- Phone Number -->
        <div>
          <label for="phoneNumber" class="block text-sm font-medium text-coffee-700 mb-1">
            Số điện thoại <span class="text-red-500">*</span>
          </label>
          <input
            id="phoneNumber"
            v-model="form.PhoneNumber"
            type="tel"
            required
            class="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.PhoneNumber }"
            placeholder="Nhập số điện thoại"
          />
          <p v-if="errors.PhoneNumber" class="text-red-500 text-xs mt-1">{{ errors.PhoneNumber[0] }}</p>
        </div>

        <!-- Email -->
        <div>
          <label for="email" class="block text-sm font-medium text-coffee-700 mb-1">
            Email
          </label>
          <input
            id="email"
            v-model="form.Email"
            type="email"
            class="w-full px-3 py-2 border border-coffee-200 rounded-lg focus:ring-2 focus:ring-coffee-500 focus:border-transparent"
            :class="{ 'border-red-500': errors.Email }"
            placeholder="Nhập email (tùy chọn)"
          />
          <p v-if="errors.Email" class="text-red-500 text-xs mt-1">{{ errors.Email[0] }}</p>
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
            variant="primary"
            class="flex-1"
            :disabled="loading"
          >
            <Loader2 v-if="loading" class="w-4 h-4 mr-2 animate-spin" />
            {{ isEditing ? 'Cập nhật' : 'Tạo mới' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { X, Loader2 } from 'lucide-vue-next'
import BaseButton from '@/components/common/BaseButton.vue'
import { customerService } from '@/services/customers'
import type { Customer, CustomerForm } from '@/types'

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
const loading = ref(false)
const errors = ref<Record<string, string[]>>({})

const form = ref<CustomerForm>({
  FullName: '',
  PhoneNumber: '',
  Email: ''
})

// Computed
const isEditing = computed(() => !!props.customer)

// Methods
const resetForm = () => {
  form.value = {
    FullName: '',
    PhoneNumber: '',
    Email: ''
  }
  errors.value = {}
}

const validateForm = (): boolean => {
  errors.value = {}
  let isValid = true

  if (!form.value.FullName.trim()) {
    errors.value.FullName = ['Họ và tên là bắt buộc']
    isValid = false
  }

  if (!form.value.PhoneNumber.trim()) {
    errors.value.PhoneNumber = ['Số điện thoại là bắt buộc']
    isValid = false
  } else {
    // Validate Vietnamese phone number format
    const phoneRegex = /^(0|\+84)[3-9]\d{8}$/
    if (!phoneRegex.test(form.value.PhoneNumber)) {
      errors.value.PhoneNumber = ['Số điện thoại không đúng định dạng Việt Nam']
      isValid = false
    }
  }

  if (form.value.Email && form.value.Email.trim()) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(form.value.Email)) {
      errors.value.Email = ['Email không đúng định dạng']
      isValid = false
    }
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }

  try {
    loading.value = true
    errors.value = {}

    if (isEditing.value && props.customer) {
      await customerService.update(props.customer.CustomerID, form.value)
      toast.success('Cập nhật khách hàng thành công')
    } else {
      await customerService.create(form.value)
      toast.success('Tạo khách hàng thành công')
    }

    emit('saved')
  } catch (error: any) {
    console.error('Error saving customer:', error)
    
    if (error.response?.data) {
      const errorData = error.response.data
      
      // Handle field validation errors
      if (errorData.FullName || errorData.PhoneNumber || errorData.Email) {
        errors.value = {
          FullName: errorData.FullName || [],
          PhoneNumber: errorData.PhoneNumber || [],
          Email: errorData.Email || []
        }
        return
      }
      
      // Handle other errors
      if (errorData.error) {
        toast.error(errorData.error)
        return
      }
    }
    
    toast.error('Có lỗi xảy ra khi lưu khách hàng')
  } finally {
    loading.value = false
  }
}

// Watchers
watch(() => props.customer, (newCustomer) => {
  if (newCustomer) {
    form.value = {
      FullName: newCustomer.FullName,
      PhoneNumber: newCustomer.PhoneNumber,
      Email: newCustomer.Email || ''
    }
  } else {
    resetForm()
  }
}, { immediate: true })

// Reset form when modal opens
watch(() => props.customer, () => {
  if (!props.customer) {
    resetForm()
  }
})
</script>
