<script setup>
import { ref, reactive, computed } from 'vue'
import { useApplicationsStore } from '@entities/applications'
import { useSettingsStore } from '@entities/settings'
import { getPasswordErrors } from '@utils/passwordRules'

import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseCheckBox from '@ui/BaseCheckBox.vue'
import FindIcon from '@icons/actions/FindIcon.vue'
import KeyIcon from '@icons/actions/KeyIcon.vue'

const appStore = useApplicationsStore()
const settingsStore = useSettingsStore()

const activeAccessTab = ref('status')
const showPassword = ref(false)
const showAccessCode = ref(false)
const accessCode = ref('')
const isCodeVerified = ref(false)

const form = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

const statusResponse = reactive({
  title: '',
  text: '',
  type: '',
})

const passwordErrors = computed(() => getPasswordErrors(form.password))

const confirmPasswordError = computed(() => {
  if (form.confirmPassword && form.password !== form.confirmPassword) {
    return 'Пароли не совпадают'
  }
  return ''
})

const canSubmitApplication = computed(() => {
  return (
    passwordErrors.value.length === 0 &&
    !confirmPasswordError.value &&
    form.email &&
    form.password &&
    form.confirmPassword
  )
})

const verifyAccessCode = async () => {
  if (!accessCode.value.trim()) {
    return
  }
  const response = await settingsStore.verifyCode(accessCode.value)
  isCodeVerified.value = response.success
}

const clearForm = () => {
  form.email = ''
  form.password = ''
  form.confirmPassword = ''
  accessCode.value = ''
  isCodeVerified.value = false
  showAccessCode.value = false
  statusResponse.title = ''
  statusResponse.text = ''
  statusResponse.type = ''
}

const selectAccessTab = (tab) => {
  activeAccessTab.value = tab
  clearForm()
}

const handleSubmit = async () => {
  if (activeAccessTab.value === 'status') {
    const result = await appStore.checkApplicationStatus(form.email)
    const statusMap = {
      предоставлен: [
        'Доступ предоставлен',
        'Поздравляем! Ваша заявка одобрена. Теперь вы можете войти в систему.',
        'granted',
      ],
      рассматривается: [
        'Заявка на рассмотрении',
        'Ваша заявка находится на рассмотрении у администратора. Решение будет принято в ближайшее время.',
        'pending',
      ],
      отклонён: [
        'Доступ отклонен',
        'К сожалению, ваша заявка была отклонена администратором. Для выяснения причин обратитесь лично.',
        'denied',
      ],
      отсутствует: [
        'Заявка не найдена',
        'Заявка с указанным email не найдена. Пожалуйста, проверьте правильность введенного адреса или подайте новую заявку.',
        'not-found',
      ],
    }
    const [title = '', text = '', type = ''] = statusMap[result.status] || []
    Object.assign(statusResponse, { title, text, type })
  } else {
    await appStore.submitApplication({
      email: form.email,
      password: form.password,
      confirm_password: form.confirmPassword,
      registration_code: accessCode.value,
    })
    activeAccessTab.value = 'status'
    clearForm()
  }
}
</script>

<template>
  <div class="access-container">
    <div class="access-tab-panel">
      <button
        class="access-tab-button"
        :class="{ active: activeAccessTab === 'status' }"
        @click="selectAccessTab('status')"
      >
        Статус заявки
      </button>
      <button
        class="access-tab-button"
        :class="{ active: activeAccessTab === 'application' }"
        @click="selectAccessTab('application')"
      >
        Подача заявки
      </button>
    </div>

    <div class="description">
      <template v-if="activeAccessTab === 'status'">
        Чтобы узнать решение администратора по заявке, введите свой адрес электронной почты в
        соответствующее поле
      </template>
      <template v-else-if="!isCodeVerified">
        Для подачи заявки введите код доступа, полученный от администратора
      </template>
      <template v-else>Заполните и отправьте заявку на доступ</template>
    </div>

    <!-- Статус заявки -->
    <div v-if="activeAccessTab === 'status'" class="form-wrapper">
      <form @submit.prevent="handleSubmit">
        <div class="form-fields">
          <BaseInput
            v-model="form.email"
            type="email"
            label="Почта"
            label-position="left"
            placeholder="Введите вашу почту"
            name="email"
            autocomplete="username"
            required
          />
        </div>

        <div v-if="statusResponse.type" class="status-response" :class="statusResponse.type">
          <div class="status-content">
            <span class="status-title">{{ statusResponse.title }}</span>
            <p class="status-text">{{ statusResponse.text }}</p>
          </div>
        </div>

        <div class="form-button">
          <BaseButton
            class="custom-button"
            type="submit"
            variant="primary"
            size="large"
            :loading="appStore.loading"
          >
            <template #icon-left><FindIcon /></template>
            Проверить
          </BaseButton>
        </div>
      </form>
    </div>

    <!-- Подача заявки -->
    <div v-if="activeAccessTab === 'application'" class="form-wrapper">
      <!-- Код доступа -->
      <div v-if="!isCodeVerified">
        <form @submit.prevent="verifyAccessCode">
          <div class="form-fields">
            <BaseInput
              v-model="accessCode"
              :type="showAccessCode ? 'text' : 'password'"
              label="Код доступа"
              label-position="left"
              placeholder="Введите код доступа"
              name="access-code"
              autocomplete="one-time-code"
              required
            />
            <div class="password-toggle">
              <BaseCheckBox v-model="showAccessCode"> Показать код </BaseCheckBox>
            </div>
          </div>
          <div class="form-button">
            <BaseButton
              type="submit"
              class="custom-button"
              variant="primary"
              size="large"
              :loading="settingsStore.loading"
            >
              <template #icon-left><KeyIcon /></template>
              Проверить код
            </BaseButton>
          </div>
        </form>
      </div>

      <!-- Форма заявки -->
      <div v-else>
        <form @submit.prevent="handleSubmit">
          <div class="form-fields">
            <BaseInput
              v-model="form.email"
              type="email"
              label="Почта"
              label-position="left"
              placeholder="Введите вашу почту"
              name="email"
              autocomplete="username"
              required
            />
            <BaseInput
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              label="Пароль"
              label-position="left"
              placeholder="Введите ваш пароль"
              :error="passwordErrors.length > 0 ? passwordErrors[0] : ''"
              name="new-password"
              autocomplete="new-password"
              required
            />
            <BaseInput
              v-model="form.confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              label="Пароль"
              label-position="left"
              placeholder="Подтвердите пароль"
              :error="confirmPasswordError"
              name="new-password"
              autocomplete="new-password"
              required
            />
            <div class="password-toggle">
              <BaseCheckBox v-model="showPassword"> Показать пароли </BaseCheckBox>
            </div>
          </div>
          <div class="form-button">
            <BaseButton
              class="custom-button"
              type="submit"
              variant="primary"
              size="large"
              :loading="appStore.loading"
              :disabled="!canSubmitApplication"
            >
              <template #icon-left><KeyIcon /></template>
              Отправить заявку
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.access-container {
  margin: 40px 0px 0px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 40px;
  width: 100%;
}

.access-tab-panel {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: flex-start;
  padding: 0;
  gap: 30px;
}

.access-tab-button {
  display: flex;
  flex-direction: column;
  padding: 8px 31px 14px;
  height: auto;
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--secondary);
  font: var(--medium-text);
  position: relative;
  transition: all 0.3s ease;
}

.access-tab-button::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 1px;
  background: var(--secondary);
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.access-tab-button.active::after {
  width: 100%;
}

.description {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  color: var(--dark);
  font: var(--small-text);
  height: auto;
  padding: 0 20px;
  line-height: 1.5;
  max-width: 90%;
}

.form-wrapper {
  width: 460px;
}

.form-fields {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.form-button {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: flex-end;
  margin: 100px 0px 0px;
  gap: 10px;
  width: 100%;
  height: 50px;
}

.custom-button {
  width: 250px;
}

.password-toggle {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  padding: 0;
  gap: 10px;
  width: 100%;
  height: 24px;
}

.status-response {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  text-align: center;
  min-height: 80px;
  width: 100%;
  border: 2px solid transparent;
}

.status-response.pending {
  border-color: color-mix(in srgb, var(--info) 30%, transparent);
  color: var(--info);
}

.status-response.granted {
  border-color: color-mix(in srgb, var(--success) 30%, transparent);
  color: var(--success);
}

.status-response.denied {
  border-color: color-mix(in srgb, var(--error) 30%, transparent);
  color: var(--error);
}

.status-response.not-found {
  border-color: color-mix(in srgb, var(--warning) 30%, transparent);
  color: var(--warning);
}

.status-content {
  white-space: pre-line;
  line-height: 1.5;
  font: var(--small-text);
}

.status-title {
  font: var(--small-text);
}

.status-text {
  margin: 8px;
  font-size: 14px;
}

@media (max-width: 768px) {
  .form-wrapper {
    width: 80%;
    padding: 0 20px;
  }

  .access-tab-button {
    padding: 8px 16px;
    font-size: 14px;
  }

  .description {
    max-width: 90%;
    padding: 0 15px;
  }

  .form-button {
    margin: 60px 0px 0px;
  }

  .custom-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .access-tab-panel {
    flex-direction: column;
    gap: 10px;
    height: auto;
  }

  .access-tab-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
