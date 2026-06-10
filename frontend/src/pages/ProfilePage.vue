<script setup>
import { useRouter } from 'vue-router'
import Header from '@/app/layout/StartHeader.vue'
import ProfileSection from '@profile/ProfileSection.vue'
import ArrowLeftIcon from '@icons/actions/ArrowLeftIcon.vue'
import BaseButton from '@ui/BaseButton.vue'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push({ name: 'Monitoring' })
  }
}
</script>

<template>
  <div class="dashboard-view">
    <Header />
    <main class="dashboard-content">
      <div class="container">
        <BaseButton variant="ghost" size="medium" label="Назад" class="back-button" @click="goBack">
          <template #icon-left>
            <ArrowLeftIcon />
          </template>
        </BaseButton>
        <ProfileSection />
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.dashboard-content {
  flex: 1;
  padding: 40px 20px;
  background: var(--bg);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.back-button {
  padding: 16px;
}

@media (max-width: 768px) {
  .dashboard-content {
    padding: 24px 16px;
  }

  .back-button {
    margin-bottom: 16px;
  }
}
</style>
