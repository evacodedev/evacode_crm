# EvaCode Sales CRM — локальный MVP заказов

Рабочее место Sales: логин, реквизиты клиента, адрес доставки, корзина с **персональными группами консультанта**.  
Стек: Django 5 + DRF + Postgres + Celery/Redis + Vue 3 (Vite).  
**Только локально** (Docker Compose). VPS не деплоим. Business.Ru — stub.

Спека: Context `docs/mvp-sales-order-tool.md` (проект IT EvaCode).

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

| Сервис | URL |
|--------|-----|
| Web UI | http://127.0.0.1:43123 |
| API | http://127.0.0.1:8000/api/ |
| Admin | http://127.0.0.1:8000/admin/ |

### Демо-пользователь

| Поле | Значение |
|------|----------|
| Логин | `sales` |
| Пароль | `sales123` (или `DEMO_SALES_PASSWORD` из `.env`) |

При старте API: migrate + `seed_demo` (категории, товары, группа «Частые позиции»).

### Windows

Рекомендуется **Docker Desktop + WSL2**. Команды те же из WSL-терминала в каталоге репо.

## Без Docker (dev fallback)

Нужны Python 3.12+, Node 20+, опционально Postgres/Redis.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# в .env:
# USE_SQLITE=1
# CELERY_TASK_ALWAYS_EAGER=1
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8000
```

```bash
cd web && npm install
VITE_API_BASE=http://127.0.0.1:8000 npm run dev -- --port 43123
```

## API кратко

- `POST /api/auth/login/` `{username, password}` → token  
- `GET /api/auth/me/` · `POST /api/auth/logout/`  
- `GET /api/catalog/products/` · `GET/POST /api/catalog/groups/`  
- `PUT /api/catalog/groups/{id}/products/` `{product_ids:[…]}`  
- `GET/POST /api/orders/`

## Business.Ru

`integrations/business_ru.py` — stub. Celery task помечает заказ как `stubbed`.  
Live credentials **не** кладём в репо. TODO: реальный клиент + retries.

## Структура

```
accounts/     auth API
catalog/      Product, Category, ConsultantGroup
orders/       Order, OrderLine, Celery task
integrations/ Business.Ru stub
web/          Vue 3 SPA
docker-compose.yml
```

## Демо-чеклист Sales

1. `docker compose up --build`
2. Открыть http://127.0.0.1:43123
3. Войти `sales` / `sales123`
4. «Мои группы» — демо-группа; при желании добавить товары
5. «Новый заказ» — клиент + адрес
6. Товары из группы / «Все товары» → корзина → «Оформить»
7. «Заказы» — новый заказ, синк = Stub Business.Ru
