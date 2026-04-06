<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="text-center">
      <div class="text-8xl mb-6">☕</div>
      <h1 class="text-6xl font-bold text-coffee-700 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-coffee-600 mb-4">Trang không tìm thấy</h2>
      <p class="text-coffee-500 mb-8 max-w-md mx-auto">
        Xin lỗi, trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <BaseButton @click="$router.push('/dashboard')" variant="primary">
          <Home class="w-4 h-4 mr-2" />
          Về trang chủ
        </BaseButton>
        <BaseButton @click="$router.go(-1)" variant="outline">
          <ArrowLeft class="w-4 h-4 mr-2" />
          Quay lại
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Home, ArrowLeft } from 'lucide-vue-next'
import BaseButton from '@/components/common/BaseButton.vue'
</script>
