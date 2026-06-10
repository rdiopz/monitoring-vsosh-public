<script setup>
import { useRouter } from 'vue-router'
import BaseButton from '@ui/BaseButton.vue'
const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="large-text text-accent">404</h1>
      <h2 class="medium-text text-secondary">Страница не найдена</h2>
      <p class="small-text text-tertiary">
        К сожалению, запрашиваемая страница не существует.<br />
        Возможно, она была перемещена или удалена.
      </p>

      <div class="button-group">
        <router-link to="/" class="router-link-button">
          <BaseButton variant="primary" size="medium">Главная</BaseButton>
        </router-link>

        <BaseButton variant="outline" size="medium" @click="goBack">Назад</BaseButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  background: var(--white);
}

.not-found-content {
  max-width: 500px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.router-link-button {
  display: contents;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 300px;
  margin-top: 1rem;
}

.router-link-button {
  text-decoration: none;
  width: 100%;
}
</style>
