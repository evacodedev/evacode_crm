<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref('')
const orders = ref([])
const groups = ref([])
const tab = ref('week')
const quick = ref('')
const weekAnchor = ref(startOfWeek(new Date()))

const HOUR_START = 8
const HOUR_END = 20
const ROW = 46

const name = computed(() => auth.user?.first_name || auth.user?.username || '')
const hello = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Доброе утро'
  if (h < 18) return 'Добрый день'
  return 'Добрый вечер'
})

const counts = computed(() => {
  const list = orders.value
  return {
    total: list.length,
    synced: list.filter((o) => o.business_ru_sync_status === 'stubbed').length,
    pending: list.filter((o) => o.business_ru_sync_status === 'pending').length,
    failed: list.filter((o) => o.business_ru_sync_status === 'failed').length,
    draft: list.filter((o) => o.status === 'draft').length,
    groups: groups.value.length,
  }
})

const donut = computed(() => {
  const parts = [
    { value: counts.value.synced, color: '#3dce8a' },
    { value: counts.value.pending, color: '#5b8def' },
    { value: counts.value.draft, color: '#8b6cff' },
    { value: counts.value.failed, color: '#f5a04a' },
  ]
  const total = parts.reduce((s, p) => s + p.value, 0)
  if (!total) return 'conic-gradient(#e7ebf3 0 100%)'
  let acc = 0
  const gap = 1.4
  const stops = []
  for (const p of parts) {
    if (!p.value) continue
    const span = (p.value / total) * 100
    const end = acc + Math.max(span - gap, 0.4)
    stops.push(`${p.color} ${acc}% ${end}%`)
    stops.push(`#fff ${end}% ${acc + span}%`)
    acc += span
  }
  return `conic-gradient(${stops.join(',')})`
})

const recent = computed(() => {
  const q = String(route.query.q || '').trim().toLowerCase()
  return orders.value
    .filter((o) => !q || `${o.client_name} ${o.client_phone} ${o.id}`.toLowerCase().includes(q))
    .slice(0, 6)
})

const hours = computed(() => {
  const list = []
  for (let h = HOUR_START; h < HOUR_END; h += 1) list.push(`${String(h).padStart(2, '0')}:00`)
  return list
})

const days = computed(() => {
  const labels = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
  const today = new Date()
  return labels.map((label, i) => {
    const date = new Date(weekAnchor.value)
    date.setDate(date.getDate() + i)
    return {
      label,
      num: date.getDate(),
      today: date.toDateString() === today.toDateString(),
    }
  })
})

const weekEvents = computed(() => {
  const start = weekAnchor.value.getTime()
  const end = start + 7 * 86400000
  const buckets = {}
  return orders.value
    .map((order) => {
      const d = new Date(order.created_at)
      const t = d.getTime()
      if (t < start || t >= end) return null
      let hour = d.getHours() + d.getMinutes() / 60
      if (hour < HOUR_START) hour = HOUR_START
      if (hour > HOUR_END - 1) hour = HOUR_END - 1
      const day = d.getDay()
      const key = `${day}-${Math.floor(hour)}`
      const idx = buckets[key] || 0
      buckets[key] = idx + 1
      const top = (hour - HOUR_START) * ROW + idx * 8
      return {
        id: order.id,
        title: order.client_name,
        style: {
          top: `${top}px`,
          height: `${ROW - 8}px`,
          left: `calc(${day} * (100% / 7) + 4px)`,
          width: `calc(100% / 7 - 8px)`,
        },
      }
    })
    .filter(Boolean)
})

const monthValue = computed(() => weekAnchor.value.getMonth())
const yearValue = computed(() => weekAnchor.value.getFullYear())
const years = computed(() => {
  const y = new Date().getFullYear()
  return [y - 1, y, y + 1]
})
const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

function startOfWeek(d) {
  const x = new Date(d)
  x.setHours(0, 0, 0, 0)
  x.setDate(x.getDate() - x.getDay())
  return x
}

function setMonth(month) {
  weekAnchor.value = startOfWeek(new Date(yearValue.value, Number(month), 1))
}
function setYear(year) {
  weekAnchor.value = startOfWeek(new Date(Number(year), monthValue.value, 1))
}
function shiftWeek(dir) {
  const next = new Date(weekAnchor.value)
  next.setDate(next.getDate() + dir * 7)
  weekAnchor.value = next
}

function money(n) {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(n)
}

function tone(order) {
  if (order.business_ru_sync_status === 'failed') return 'red'
  if (order.business_ru_sync_status === 'pending') return 'orange'
  if (order.status === 'draft') return 'blue'
  return 'green'
}

function openOrder(id) {
  router.push({ name: 'orders', query: { open: id } })
}

function startQuick() {
  const client = quick.value.trim()
  router.push({ name: 'order', query: client ? { client } : {} })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [o, g] = await Promise.all([api('/api/orders/'), api('/api/catalog/groups/')])
    orders.value = o
    groups.value = g
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="dash">
    <div class="action-row">
      <RouterLink class="action action-blue" :to="{ name: 'order' }">
        <span class="action-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </span>
        <span><strong>Новый заказ</strong><small>Клиент, адрес и корзина</small></span>
      </RouterLink>
      <RouterLink class="action action-orange" :to="{ name: 'orders' }">
        <span class="action-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M7 7h10v12H7zM9 7V5h6v2" stroke="currentColor" stroke-width="1.8"/></svg>
        </span>
        <span><strong>Заказы</strong><small>{{ counts.total }} в вашем списке</small></span>
      </RouterLink>
      <RouterLink class="action action-green" :to="{ name: 'groups' }">
        <span class="action-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M4 19V5h6l2 2h8v12H4Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>
        </span>
        <span><strong>Группы</strong><small>{{ counts.groups }} персональных групп</small></span>
      </RouterLink>
      <RouterLink class="action action-purple" :to="{ name: 'orders' }">
        <span class="action-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 3l2.2 6.4L21 12l-6.8 2.6L12 21l-2.2-6.4L3 12l6.8-2.6L12 3Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></svg>
        </span>
        <span><strong>Синхронизация</strong><small>Статус Business.Ru</small></span>
      </RouterLink>
    </div>

    <p v-if="error" class="error" style="grid-column: 1 / -1">{{ error }}</p>

    <section class="card hero">
      <h2>{{ hello }}, {{ name }}!</h2>
      <p class="muted">Заказы, группы товаров и отправка в Business.Ru — на одном экране.</p>
      <div class="hero-body">
        <div class="donut-wrap">
          <div class="donut" :style="{ background: donut }">
            <div class="donut-hole">
              <strong>{{ counts.total }}</strong>
              <span>Всего заказов</span>
            </div>
          </div>
        </div>
        <div class="stat-grid">
          <div class="stat">
            <span class="pill green">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            </span>
            <div><b>{{ counts.synced }}</b><span>В Business.Ru</span></div>
          </div>
          <div class="stat">
            <span class="pill blue">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.8"/><path d="M12 8v5l3 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            </span>
            <div><b>{{ counts.pending }}</b><span>Ожидают</span></div>
          </div>
          <div class="stat">
            <span class="pill purple">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M6 7h12v12H6z" stroke="currentColor" stroke-width="1.8"/><path d="M9 7V5h6v2" stroke="currentColor" stroke-width="1.8"/></svg>
            </span>
            <div><b>{{ counts.draft }}</b><span>Черновики</span></div>
          </div>
          <div class="stat">
            <span class="pill orange">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 8v5M12 17h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.8"/></svg>
            </span>
            <div><b>{{ counts.failed }}</b><span>Ошибки синка</span></div>
          </div>
        </div>
      </div>
      <p v-if="loading" class="muted" style="margin: 12px 0 0">Загрузка…</p>
    </section>

    <aside class="rail">
      <section class="card">
        <h3>Новый заказ</h3>
        <RouterLink class="dropzone" :to="{ name: 'order' }">
          <span class="pill blue">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </span>
          <span>Клиент, доставка и товары из групп.<br><strong>Открыть форму</strong></span>
        </RouterLink>
        <input
          v-model="quick"
          class="quick-input"
          placeholder="Имя клиента"
          @keydown.enter="startQuick"
        />
      </section>
      <section class="card">
        <h3>Последние заказы</h3>
        <ul class="doc-list">
          <li v-for="o in recent" :key="o.id">
            <button class="doc-row" type="button" @click="openOrder(o.id)">
              <span class="doc-ico" :class="`pill ${tone(o)}`">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M7 3h7l5 5v13H7V3Z" stroke="currentColor" stroke-width="1.7"/><path d="M14 3v5h5" stroke="currentColor" stroke-width="1.7"/></svg>
              </span>
              <span>
                <strong>{{ o.client_name }}</strong>
                <span>№{{ o.id }} · {{ money(o.total_amount) }}</span>
              </span>
            </button>
          </li>
        </ul>
        <p v-if="!loading && !recent.length" class="muted">Пока нет заказов.</p>
      </section>
    </aside>

    <section class="card cal-card">
      <div class="tabs">
        <button type="button" class="tab" :class="{ active: tab === 'week' }" @click="tab = 'week'">Заказы недели</button>
        <button type="button" class="tab" :class="{ active: tab === 'groups' }" @click="tab = 'groups'">Группы</button>
        <button type="button" class="tab" :class="{ active: tab === 'sync' }" @click="tab = 'sync'">Синхронизация</button>
      </div>

      <template v-if="tab === 'week'">
        <div class="cal-nav">
          <button class="ghost" type="button" aria-label="Предыдущая неделя" @click="shiftWeek(-1)">‹</button>
          <select :value="yearValue" aria-label="Год" @change="setYear($event.target.value)">
            <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
          </select>
          <select :value="monthValue" aria-label="Месяц" @change="setMonth($event.target.value)">
            <option v-for="(m, i) in monthNames" :key="m" :value="i">{{ m }}</option>
          </select>
          <button class="ghost" type="button" aria-label="Следующая неделя" @click="shiftWeek(1)">›</button>
        </div>
        <div class="cal-scroll">
          <div class="cal-sheet">
          <div class="cal-head">
            <span v-for="d in days" :key="d.label" :class="{ 'is-today': d.today }">
              {{ d.label }}
              <b>{{ d.num }}</b>
            </span>
          </div>
          <div class="cal-body">
            <div class="cal-hours">
              <span v-for="h in hours" :key="h">{{ h }}</span>
            </div>
            <div class="cal-cols">
              <div v-for="(d, i) in days" :key="d.label" class="cal-col" :class="{ 'is-today': d.today }">
                <div v-for="h in hours" :key="`${i}-${h}`" class="cal-cell" />
              </div>
              <button
                v-for="ev in weekEvents"
                :key="ev.id"
                class="cal-event"
                type="button"
                :style="ev.style"
                @click="openOrder(ev.id)"
              >
                {{ ev.title }}
              </button>
            </div>
          </div>
          </div>
        </div>
      </template>

      <div v-else-if="tab === 'groups'" class="mini-list">
        <article v-for="g in groups" :key="g.id">
          <strong>{{ g.name }}</strong>
          <p class="muted" style="margin: 4px 0 0">{{ g.items.length }} товаров</p>
        </article>
        <p v-if="!groups.length" class="muted">Групп пока нет.</p>
      </div>

      <div v-else class="mini-list">
        <article v-for="o in orders.slice(0, 8)" :key="o.id">
          <strong>№{{ o.id }} · {{ o.client_name }}</strong>
          <p class="muted" style="margin: 4px 0 0">{{ o.business_ru_sync_message || o.business_ru_sync_status }}</p>
        </article>
        <p v-if="!orders.length" class="muted">Синхронизировать пока нечего.</p>
      </div>
    </section>
  </div>
</template>
