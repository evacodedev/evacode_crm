<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const username = ref('sales')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await auth.login(username.value.trim(), password.value)
    router.push({ name: 'order' })
  } catch (e) {
    error.value = e.message || 'Не удалось войти'
  }
}
</script>

<template>
  <div class="login-wrap">
    <form class="panel login-card stack" @submit.prevent="submit">
      <div>
        <h1>Вход для Sales</h1>
        <p class="muted">Рабочее место оформления заказов EvaCode</p>
      </div>
      <label>
        Логин
        <input v-model="username" autocomplete="username" required />
      </label>
      <label>
        Пароль
        <input v-model="password" type="password" autocomplete="current-password" required />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn" type="submit" :disabled="auth.loading">
        {{ auth.loading ? 'Вход…' : 'Войти' }}
      </button>
      <p class="muted">Демо: sales / sales123</p>
    </form>
  </div>
</template>
