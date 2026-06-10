<script setup>
import { useThemeStore } from '@stores/theme'
import MoonIcon from '@icons/actions/MoonIcon.vue'
import SunIcon from '@icons/actions/SunIcon.vue'

const themeStore = useThemeStore()
const toggleTheme = () => themeStore.toggleTheme()
</script>

<template>
  <header class="header">
    <div class="header-content">
      <!-- Левая часть с логотипом -->
      <div class="left-section">
        <img class="logo" src="@/assets/logo_onfim.svg" alt="Логотип Онфим" />
        <h1 class="title large-text">
          Мониторинг <span class="text-accent">ВсОШ</span> по
          <span class="text-accent">Новгородской области</span>
        </h1>
      </div>
      <!-- Правая часть с переключением темы -->
      <button class="theme-toggle" @click="toggleTheme" aria-label="Переключить тему">
        <MoonIcon v-if="!themeStore.isDark" />
        <SunIcon v-else />
        <span class="theme-text medium-text">Тема</span>
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: var(--gradient-header);
  padding: 8.5px 32px;
  border: 1px solid var(--secondary);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 auto;
}

.left-section {
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  width: 100px;
  height: 100px;
  object-fit: contain;
}

.title {
  color: var(--on-header);
  margin: 0;
}

.theme-toggle {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  background: var(--theme-button-color);
  border: 1px solid var(--secondary);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.theme-toggle:hover {
  transform: translateY(-1px);
}

.theme-toggle svg {
  color: var(--on-header);
}

.theme-text {
  color: var(--on-header);
}

@media (max-width: 768px) {
  .header {
    padding: 4.25px 8px;
  }
  .header-content {
    padding: 0 16px;
  }

  .left-section {
    gap: 20px;
  }

  .logo {
    width: 60px;
    height: 60px;
  }

  .title {
    font-size: 16px;
  }

  .theme-text {
    display: none;
  }

  .theme-toggle {
    padding: 8px;
  }
}
</style>
