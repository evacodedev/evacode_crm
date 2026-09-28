<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref('')

const groups = ref([])
const products = ref([])
const activeTab = ref('group') // group id or 'all'
const search = ref('')

const form = ref({
  client_name: '',
  client_phone: '',
  client_email: '',
  client_note: '',
  delivery_country: 'Россия',
  delivery_city: '',
  delivery_street: '',
  delivery_postal: '',
})

const cart = ref([]) // { product, quantity }

const visibleProducts = computed(() => {
  const q = search.value.trim().toLowerCase()
  let list = []
  if (activeTab.value === 'all') {
    list = products.value
  } else {
    const g = groups.value.find((x) => String(x.id) === String(activeTab.value))
    list = g ? g.items.map((i) => i.product) : []
  }
  if (!q) return list
  return list.filter(
    (p) =>
      p.name.toLowerCase().includes(q) ||
      p.sku.toLowerCase().includes(q) ||
      (p.category_name || '').toLowerCase().includes(q),
  )
})

const cartTotal = computed(() =>
  cart.value.reduce((sum, line) => sum + Number(line.product.price) * line.quantity, 0),
)

function money(n) {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(n)
}

function addToCart(product) {
  const existing = cart.value.find((l) => l.product.id === product.id)
  if (existing) existing.quantity += 1
  else cart.value.push({ product, quantity: 1 })
}

function removeFromCart(productId) {
  cart.value = cart.value.filter((l) => l.product.id !== productId)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [g, p] = await Promise.all([
      api('/api/catalog/groups/'),
      api('/api/catalog/products/'),
    ])
    groups.value = g
    products.value = p
    if (g.length) activeTab.value = g[0].id
    else activeTab.value = 'all'
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function submitOrder() {
  error.value = ''
  success.value = ''
  if (!cart.value.length) {
    error.value = 'Добавьте товары в корзину.'
    return
  }
  submitting.value = true
  try {
    const order = await api('/api/orders/', {
      method: 'POST',
      body: JSON.stringify({
        ...form.value,
        line_items: cart.value.map((l) => ({
          product_id: l.product.id,
          quantity: l.quantity,
        })),
      }),
    })
    success.value = `Заказ №${order.id} оформлен на сумму ${money(order.total_amount)}.`
    cart.value = []
    setTimeout(() => router.push({ name: 'orders' }), 900)
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <h1>Новый заказ</h1>
    <p class="muted">Реквизиты клиента, адрес доставки и подбор товаров из ваших групп.</p>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="ok">{{ success }}</p>
    <p v-if="loading" class="muted">Загрузка каталога…</p>

    <div v-else class="grid-2">
      <div class="stack">
        <section class="panel stack">
          <h2>Клиент</h2>
          <label>ФИО <input v-model="form.client_name" required /></label>
          <div class="row" style="align-items: stretch">
            <label style="flex: 1">Телефон <input v-model="form.client_phone" required /></label>
            <label style="flex: 1">Email <input v-model="form.client_email" type="email" /></label>
          </div>
          <label>Комментарий <textarea v-model="form.client_note" /></label>
        </section>

        <section class="panel stack">
          <h2>Адрес доставки</h2>
          <div class="row" style="align-items: stretch">
            <label style="flex: 1">Страна <input v-model="form.delivery_country" /></label>
            <label style="flex: 1">Город <input v-model="form.delivery_city" required /></label>
          </div>
          <label>Улица, дом, квартира <input v-model="form.delivery_street" required /></label>
          <label>Индекс <input v-model="form.delivery_postal" style="max-width: 180px" /></label>
        </section>

        <section class="panel">
          <h2>Товары</h2>
          <div class="tabs">
            <button
              v-for="g in groups"
              :key="g.id"
              type="button"
              class="tab"
              :class="{ active: activeTab === g.id }"
              @click="activeTab = g.id"
            >
              {{ g.name }}
            </button>
            <button
              type="button"
              class="tab"
              :class="{ active: activeTab === 'all' }"
              @click="activeTab = 'all'"
            >
              Все товары
            </button>
          </div>
          <label>
            Поиск
            <input v-model="search" placeholder="название или артикул" />
          </label>
          <div class="product-list" style="margin-top: 0.75rem">
            <div v-for="p in visibleProducts" :key="p.id" class="product-row">
              <div>
                <strong>{{ p.name }}</strong>
                <span class="muted">{{ p.sku }} · {{ p.category_name || 'без категории' }}</span>
              </div>
              <div class="price">{{ money(p.price) }}</div>
              <button type="button" class="btn secondary" @click="addToCart(p)">+</button>
            </div>
            <p v-if="!visibleProducts.length" class="muted">Нет товаров в этой вкладке.</p>
          </div>
        </section>
      </div>

      <aside class="panel">
        <h2>Корзина</h2>
        <div v-if="!cart.length" class="muted">Пока пусто — добавьте позиции слева.</div>
        <div v-for="line in cart" :key="line.product.id" class="cart-line">
          <div>
            <strong>{{ line.product.name }}</strong>
            <div class="muted">{{ money(line.product.price) }}</div>
          </div>
          <input
            v-model.number="line.quantity"
            class="qty"
            type="number"
            min="1"
          />
          <button type="button" class="btn secondary" @click="removeFromCart(line.product.id)">×</button>
        </div>
        <div class="total">Итого: {{ money(cartTotal) }}</div>
        <button
          class="btn"
          style="width: 100%; margin-top: 1rem"
          type="button"
          :disabled="submitting"
          @click="submitOrder"
        >
          {{ submitting ? 'Оформление…' : 'Оформить заказ' }}
        </button>
      </aside>
    </div>
  </div>
</template>
