<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const route = useRoute()

const groups = ref([])
const products = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')

const newName = ref('')
const editingId = ref(null)
const selectedIds = ref([])

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
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function createGroup() {
  message.value = ''
  error.value = ''
  if (!newName.value.trim()) return
  try {
    await api('/api/catalog/groups/', {
      method: 'POST',
      body: JSON.stringify({ name: newName.value.trim(), product_ids: [] }),
    })
    newName.value = ''
    message.value = 'Группа создана'
    await load()
  } catch (e) {
    error.value = e.message
  }
}

function startEdit(group) {
  editingId.value = group.id
  selectedIds.value = group.items.map((i) => i.product.id)
}

async function saveProducts() {
  error.value = ''
  message.value = ''
  try {
    await api(`/api/catalog/groups/${editingId.value}/products/`, {
      method: 'PUT',
      body: JSON.stringify({ product_ids: selectedIds.value }),
    })
    message.value = 'Состав группы сохранён'
    editingId.value = null
    await load()
  } catch (e) {
    error.value = e.message
  }
}

async function removeGroup(id) {
  if (!confirm('Удалить группу?')) return
  try {
    await api(`/api/catalog/groups/${id}/`, { method: 'DELETE' })
    await load()
  } catch (e) {
    error.value = e.message
  }
}

const visibleGroups = computed(() => {
  const q = String(route.query.q || '').trim().toLowerCase()
  if (!q) return groups.value
  return groups.value.filter((g) => g.name.toLowerCase().includes(q))
})

function toggleProduct(id) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((x) => x !== id)
  } else {
    selectedIds.value = [...selectedIds.value, id]
  }
}

onMounted(load)
</script>

<template>
  <div>
    <header class="page-head">
      <h1>Мои группы</h1>
      <p class="muted">Соберите свою панель групп товаров — она появится в форме заказа.</p>
    </header>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="ok">{{ message }}</p>

    <section class="panel stack">
      <h2>Новая группа</h2>
      <div class="row">
        <input v-model="newName" placeholder="Например: Хиты / Дорогие наборы" style="flex: 1" />
        <button class="btn" type="button" @click="createGroup">Создать</button>
      </div>
    </section>

    <p v-if="loading" class="muted">Загрузка…</p>

    <section v-for="g in visibleGroups" :key="g.id" class="panel" style="margin-top: 1rem">
      <div class="row" style="justify-content: space-between">
        <h2 style="margin: 0">{{ g.name }}</h2>
        <div class="row">
          <button class="btn secondary" type="button" @click="startEdit(g)">Товары</button>
          <button class="btn danger" type="button" @click="removeGroup(g.id)">Удалить</button>
        </div>
      </div>
      <ul>
        <li v-for="item in g.items" :key="item.id">
          {{ item.product.name }}
          <span class="muted">({{ item.product.sku }})</span>
        </li>
      </ul>
      <p v-if="!g.items.length" class="muted">Пока пусто — нажмите «Товары».</p>

      <div v-if="editingId === g.id" class="stack" style="margin-top: 1rem">
        <h3>Выберите товары</h3>
        <label v-for="p in products" :key="p.id" class="check-row">
          <input
            type="checkbox"
            :checked="selectedIds.includes(p.id)"
            @change="toggleProduct(p.id)"
          />
          <span>{{ p.name }} <span class="muted">{{ p.sku }}</span></span>
        </label>
        <div class="row">
          <button class="btn" type="button" @click="saveProducts">Сохранить</button>
          <button class="btn secondary" type="button" @click="editingId = null">Отмена</button>
        </div>
      </div>
    </section>
  </div>
</template>
