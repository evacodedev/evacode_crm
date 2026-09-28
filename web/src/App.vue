<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()
const showChrome = computed(() => auth.isAuthenticated && router.currentRoute.value.name !== 'login')

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div v-if="showChrome" class="shell">
    <header class="topbar">
      <div class="brand">EvaCode <span>Sales</span></div>
      <nav class="nav">
        <RouterLink :to="{ name: 'order' }">Новый заказ</RouterLink>
        <RouterLink :to="{ name: 'groups' }">Мои группы</RouterLink>
        <RouterLink :to="{ name: 'orders' }">Заказы</RouterLink>
        <span class="user-chip">{{ auth.user?.first_name || auth.user?.username }}</span>
        <button class="linkish" type="button" @click="onLogout">Выход</button>
      </nav>
    </header>
    <RouterView />
  </div>
  <RouterView v-else />
</template>
