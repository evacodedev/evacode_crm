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
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message || 'Не удалось войти'
  }
}
</script>

<template>
  <div class="login-wrap">
    <form class="panel login-card stack" @submit.prevent="submit">
      <div class="brand-row" style="padding-bottom: 0">
        <span class="brand-mark" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M5 16.5c4-1 6.5-5 7.2-9.5 3.2 2.2 5.3 5.6 5.8 9.5-3.4.4-7.6.2-13 0Z" fill="currentColor"/>
          </svg>
        </span>
        <div class="brand-name">eva<span>code</span></div>
      </div>
      <div>
        <h1>Вход для Sales</h1>
        <p class="muted">Рабочее место оформления заказов</p>
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
