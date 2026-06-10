<script setup>
import Header from '@/app/layout/StartHeader.vue'
import LoginForm from '@auth/components/LoginForm.vue'
import ApplicationAccess from '@auth/components/ApplicationAccess.vue'
import { ref } from 'vue'

const activeMainTab = ref('login')
</script>

<template>
  <div class="login-view">
    <Header />
    <main class="main-content">
      <div class="login-door">
        <div class="tab-panel">
          <button
            class="tab-button"
            :class="{ active: activeMainTab === 'login' }"
            @click="activeMainTab = 'login'"
          >
            Вход
          </button>
          <button
            class="tab-button"
            :class="{ active: activeMainTab === 'access' }"
            @click="activeMainTab = 'access'"
          >
            Получение доступа
          </button>
        </div>

        <LoginForm v-if="activeMainTab === 'login'" />
        <ApplicationAccess v-if="activeMainTab === 'access'" />
      </div>
    </main>
    <footer class="footer">
      <div class="footer-content">
        <p class="footer-text">
          Система автоматизации учёта и анализа участия обучающихся Новгородской области<br />
          в различных этапах Всероссийской олимпиады школьников
        </p>
        <p class="footer-meta">
          <span>2025-2026</span>
          <span class="separator">•</span>
          <span class="developer">Разработчик: radio parzifalov</span>
        </p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
}

.login-door {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 600px;
  min-height: 836px;
  background: var(--white);
  box-shadow: 0 0 10px var(--primary);
  border-radius: 8px;
  margin-top: 130px;
}

.tab-panel {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
  width: 100%;
  height: 61px;
  background: var(--primary);
  border-radius: 8px 8px 0 0;
}

.tab-button {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 31px;
  height: 38px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  font: var(--medium-text);
  color: var(--white);
  transition: all 0.3s ease;
}

.tab-button.active {
  background: var(--bg-tabs);
}

.tab-button:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
}

.footer {
  width: 100%;
  padding: 42px 0px;
  background-color: var(--color-background-soft);
  color: var(--text-tertiary);
  font: var(--small-text);
  text-align: center;
  margin-top: 130px;
}

.footer-content {
  max-height: 154px;
  max-width: 800px;
  margin: 0 auto;
}

.footer-text {
  margin-bottom: 12px;
}

.footer-meta {
  opacity: 0.8;
}

.separator {
  margin: 0 8px;
}

.developer {
  color: var(--primary);
}

@media (max-width: 768px) {
  .login-door {
    width: 100%;
    max-width: 400px;
  }

  .tab-button {
    padding: 8px 16px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .login-door {
    padding-bottom: 30px;
  }

  .tab-panel {
    flex-direction: column;
    height: auto;
    padding: 15px;
    gap: 10px;
  }

  .tab-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
