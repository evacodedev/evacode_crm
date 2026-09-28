<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'

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

onMounted(load)
</script>

<template>
  <div>
    <h1>Мои заказы</h1>
    <p class="muted">Заказы, оформленные вами в этом рабочем месте.</p>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">Загрузка…</p>

    <section v-else class="panel">
      <table class="table">
        <thead>
          <tr>
            <th>№</th>
            <th>Клиент</th>
            <th>Сумма</th>
            <th>Статус</th>
            <th>Business.Ru</th>
            <th>Дата</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in orders"
            :key="o.id"
            style="cursor: pointer"
            @click="openOrder(o.id)"
          >
            <td>{{ o.id }}</td>
            <td>{{ o.client_name }}</td>
            <td>{{ money(o.total_amount) }}</td>
            <td>{{ statusLabel(o.status) }}</td>
            <td>{{ syncLabel(o.business_ru_sync_status) }}</td>
            <td>{{ new Date(o.created_at).toLocaleString('ru-RU') }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="!orders.length" class="muted">Пока нет заказов.</p>
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
