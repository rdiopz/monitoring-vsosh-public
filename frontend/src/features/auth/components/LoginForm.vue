<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@entities/auth'
import BaseButton from '@ui/BaseButton.vue'
import BaseInput from '@ui/BaseInput.vue'
import BaseCheckBox from '@ui/BaseCheckBox.vue'
import DoorIcon from '@icons/actions/DoorIcon.vue'

const router = useRouter()
const authStore = useAuthStore()

const showPassword = ref(false)

const form = reactive({
  email: '',
  password: '',
})

const handleSubmit = async () => {
  try {
    await authStore.login({
      email: form.email,
      password: form.password,
    })
    router.push({ name: 'Monitoring' })
  } catch (error) {
    console.error('Auth error:', error)
  }
}
</script>

<template>
  <div class="login-form">
    <form @submit.prevent="handleSubmit">
      <div class="input-elements">
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
          name="current-password"
          autocomplete="current-password"
          required
        />

        <div class="password-toggle">
          <BaseCheckBox v-model="showPassword"> Показать пароль </BaseCheckBox>
        </div>
      </div>

      <div class="button-area">
        <BaseButton
          class="custom-button"
          type="submit"
          variant="primary"
          size="large"
          :loading="authStore.isLoading"
        >
          <template #icon-left>
            <DoorIcon />
          </template>
          Вход в систему
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<style scoped>
.login-form {
  margin: 100px 0px 0px;
  width: 100%;
  padding: 0 70px;
}

.input-elements {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 40px;
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

.button-area {
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

@media (max-width: 768px) {
  .login-form {
    padding: 0 20px;
    margin: 60px 0px 0px;
  }

  .password-toggle {
    justify-content: flex-start;
  }

  .button-area {
    margin: 60px 0px 0px;
  }
}
</style>
