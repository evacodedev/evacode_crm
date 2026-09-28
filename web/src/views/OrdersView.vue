<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const route = useRoute()

const orders = ref([])
const loading = ref(true)
const error = ref('')
const selected = ref(null)

function money(n) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(n)
}

function statusLabel(s) {
  return s === 'submitted' ? 'Оформлен' : s === 'draft' ? 'Черновик' : s
}

function syncLabel(s) {
  const map = {
    pending: 'Ожидает',
    stubbed: 'Stub Business.Ru',
    failed: 'Ошибка синка',
  }
  return map[s] || s
}

const visibleOrders = computed(() => {
  const q = String(route.query.q || '').trim().toLowerCase()
  if (!q) return orders.value
  return orders.value.filter((o) =>
    `${o.client_name} ${o.client_phone} ${o.id} ${o.delivery_city}`.toLowerCase().includes(q),
  )
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    orders.value = await api('/api/orders/')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function openOrder(id) {
  try {
    selected.value = await api(`/api/orders/${id}/`)
  } catch (e) {
    error.value = e.message
  }
}

onMounted(async () => {
  await load()
  if (route.query.open) openOrder(route.query.open)
})

watch(
  () => route.query.open,
  (id) => {
    if (id) openOrder(id)
  },
)
</script>

<template>
  <div>
    <header class="page-head">
      <h1>Мои заказы</h1>
      <p class="muted">Заказы, оформленные вами в этом рабочем месте.</p>
    </header>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">Загрузка…</p>

    <section v-else class="panel">
      <div class="order-list">
        <button
          v-for="o in visibleOrders"
          :key="o.id"
          type="button"
          class="order-card"
          :class="{ 'is-open': selected?.id === o.id }"
          @click="openOrder(o.id)"
        >
          <span>
            <strong>№{{ o.id }} · {{ o.client_name }}</strong>
            <span class="muted">{{ new Date(o.created_at).toLocaleString('ru-RU') }}</span>
          </span>
          <span class="muted">{{ statusLabel(o.status) }}</span>
          <span class="muted">{{ syncLabel(o.business_ru_sync_status) }}</span>
          <span class="price">{{ money(o.total_amount) }}</span>
        </button>
      </div>
      <p v-if="!visibleOrders.length" class="muted">Пока нет заказов.</p>
    </section>

    <section v-if="selected" class="panel" style="margin-top: 1rem">
      <h2>Заказ №{{ selected.id }}</h2>
      <p>
        {{ selected.client_name }} · {{ selected.client_phone }}
        <span v-if="selected.client_email"> · {{ selected.client_email }}</span>
      </p>
      <p class="muted">
        {{ selected.delivery_city }}, {{ selected.delivery_street }}
        <span v-if="selected.delivery_postal">, {{ selected.delivery_postal }}</span>
      </p>
      <ul>
        <li v-for="line in selected.lines" :key="line.id">
          {{ line.product_name }} × {{ line.quantity }} — {{ money(line.line_total) }}
        </li>
      </ul>
      <p class="total">Итого: {{ money(selected.total_amount) }}</p>
      <p class="muted">{{ selected.business_ru_sync_message }}</p>
    </section>
  </div>
</template>
