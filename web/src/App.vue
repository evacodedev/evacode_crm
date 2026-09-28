<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { api } from './api'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const menuOpen = ref(false)
const userOpen = ref(false)
const notesOpen = ref(false)
const search = ref('')
const searchEl = ref(null)
const notices = ref([])

const showChrome = computed(() => auth.isAuthenticated && route.name !== 'login')
const displayName = computed(() => auth.user?.first_name || auth.user?.username || 'Sales')
const initial = computed(() => displayName.value.slice(0, 1).toUpperCase())

watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false
    userOpen.value = false
    notesOpen.value = false
    search.value = typeof route.query.q === 'string' ? route.query.q : ''
  },
  { immediate: true },
)

function applySearch() {
  const q = search.value.trim()
  const name = route.name === 'dashboard' || route.name === 'login' ? 'orders' : route.name
  router.push({ name, query: q ? { q } : {} })
}

function onKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    if (window.matchMedia('(max-width: 860px)').matches) menuOpen.value = true
    searchEl.value?.focus()
  }
}

function onDocClick(e) {
  if (!e.target.closest?.('.user-row')) {
    userOpen.value = false
    notesOpen.value = false
  }
}

async function loadNotices() {
  if (!auth.isAuthenticated) return
  try {
    const orders = await api('/api/orders/')
    notices.value = orders.filter((o) => o.business_ru_sync_status === 'failed' || o.business_ru_sync_status === 'pending')
  } catch {
    notices.value = []
  }
}

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  document.addEventListener('click', onDocClick)
  loadNotices()
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.removeEventListener('click', onDocClick)
})
watch(() => route.name, loadNotices)
</script>

<template>
  <div v-if="showChrome" class="app-frame">
    <div v-if="menuOpen" class="backdrop" @click="menuOpen = false" />
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand-row">
        <span class="brand-mark" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M5 16.5c4-1 6.5-5 7.2-9.5 3.2 2.2 5.3 5.6 5.8 9.5-3.4.4-7.6.2-13 0Z" fill="currentColor"/>
          </svg>
        </span>
        <div class="brand-name">eva<span>code</span></div>
      </div>

      <div class="user-row">
        <span class="avatar" aria-hidden="true">{{ initial }}</span>
        <button class="user-btn" type="button" @click="userOpen = !userOpen; notesOpen = false">
          <span>
            <strong>{{ displayName }}</strong>
            <small>Sales</small>
          </span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <button class="icon-btn" type="button" aria-label="Уведомления" @click="notesOpen = !notesOpen; userOpen = false">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M6 9a6 6 0 1 1 12 0c0 7 3 7 3 7H3s3 0 3-7Z" stroke="currentColor" stroke-width="1.8"/>
            <path d="M10 19a2 2 0 0 0 4 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          <span v-if="notices.length" class="badge">{{ notices.length }}</span>
        </button>
        <div v-if="userOpen" class="popover user-pop">
          <button type="button" @click="onLogout">Выйти</button>
        </div>
        <div v-if="notesOpen" class="popover">
          <p v-if="!notices.length" class="muted" style="margin: 8px 10px">Нет новых уведомлений</p>
          <RouterLink
            v-for="n in notices"
            :key="n.id"
            class="note-item"
            :to="{ name: 'orders', query: { open: n.id } }"
          >
            <strong>Заказ №{{ n.id }}</strong>
            <span>{{ n.client_name }} · {{ n.business_ru_sync_status === 'failed' ? 'ошибка синка' : 'ожидает синк' }}</span>
          </RouterLink>
        </div>
      </div>

      <form class="search" @submit.prevent="applySearch">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="11" cy="11" r="7" stroke="#8b93a7" stroke-width="2"/>
          <path d="M16 16l5 5" stroke="#8b93a7" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <input ref="searchEl" v-model="search" type="search" placeholder="Поиск…" aria-label="Поиск" />
        <span class="kbd">Ctrl K</span>
      </form>

      <nav class="side-nav">
        <RouterLink class="nav-link" :to="{ name: 'dashboard' }">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.8"/><rect x="13" y="3" width="8" height="5" rx="2" stroke="currentColor" stroke-width="1.8"/><rect x="13" y="10" width="8" height="11" rx="2" stroke="currentColor" stroke-width="1.8"/><rect x="3" y="13" width="8" height="8" rx="2" stroke="currentColor" stroke-width="1.8"/></svg>
          Обзор
        </RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'orders' }">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 6h16M4 12h16M4 18h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          Заказы
        </RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'order' }">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          Новый заказ
        </RouterLink>
        <RouterLink class="nav-link" :to="{ name: 'groups' }">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM16.5 11.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5ZM3.5 19c.6-2.4 2.6-3.5 4.5-3.5s3.9 1.1 4.5 3.5M14 15.5c1.4 0 3.2.8 3.8 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          Мои группы
        </RouterLink>
      </nav>

      <div class="side-foot">
        <button type="button" @click="onLogout">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M10 7V5a2 2 0 0 1 2-2h7v18h-7a2 2 0 0 1-2-2v-2" stroke="currentColor" stroke-width="1.8"/><path d="M4 12h10M11 8l4 4-4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Выход
        </button>
      </div>
    </aside>

    <main class="workspace">
      <div class="mobile-bar">
        <button class="icon-btn" type="button" aria-label="Меню" @click="menuOpen = true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        </button>
        <strong>evacode</strong>
      </div>
      <RouterView />
    </main>
  </div>
  <RouterView v-else />
</template>
