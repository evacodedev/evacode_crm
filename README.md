# EvaCode Sales CRM — локальный MVP заказов

Рабочее место Sales: логин, реквизиты клиента, адрес доставки, корзина с **персональными группами консультанта**.  
Стек: Django 5 + DRF + Postgres + Celery/Redis + Vue 3 (Vite).  
**Только локально** (Docker Compose). VPS не деплоим. Business.Ru — stub.

Канонический репозиторий: [evacodedev/evacode_crm](https://github.com/evacodedev/evacode_crm)  
Локальный путь (Windows): `C:\work\site\evacodeCRM`

---

## Быстрый старт (Windows PowerShell)

Нужны **Docker Desktop** (WSL2 backend) и Git. Origin CLI / Ubuntu отдельно не нужны.

```powershell
cd C:\work\site
git clone https://github.com/evacodedev/evacode_crm.git evacodeCRM
cd evacodeCRM
copy .env.example .env
docker compose up --build
```

| Сервис | URL |
|--------|-----|
| Web UI | http://127.0.0.1:43123 |
| API | http://127.0.0.1:8000/api/ |
| Admin | http://127.0.0.1:8000/admin/ |

Если порт 8000 занят (локальная витрина), в `.env` задайте `API_HOST_PORT=8001` — тогда API и админка будут на http://127.0.0.1:8001.

### Демо-пользователь

| Поле | Значение |
|------|----------|
| Логин | `sales` |
| Пароль | `sales123` (или `DEMO_SALES_PASSWORD` из `.env`) |

При старте API: migrate + `seed_demo` (категории, товары, группа «Частые позиции»).  
`seed_demo` каждый раз выставляет пароль из `DEMO_SALES_PASSWORD` (по умолчанию `sales123`).

### Если «не заходит»

1. Docker Desktop запущен; в каталоге репо есть файл `.env` (`copy .env.example .env`).
2. Открывай именно http://127.0.0.1:43123 (не другой порт / не `file://`).
3. Проверки в PowerShell из `C:\work\site\evacodeCRM`:

```powershell
docker compose ps
docker compose logs api --tail 80
# Должно быть: Seed OK. User sales / sales123
curl.exe -s -X POST http://127.0.0.1:8000/api/auth/login/ -H "Content-Type: application/json" -d "{\"username\":\"sales\",\"password\":\"sales123\"}"
```

Ожидаемый ответ API — JSON с `"token": "..."`. Если так, а в браузере нет — обнови страницу с очисткой кэша (Ctrl+F5) или другой браузер.

Пересоздать пользователя и подтянуть фикс прокси:

```powershell
git pull
docker compose down
docker compose up --build
# или только seed:
docker compose exec api python manage.py seed_demo
```

---

## Без Docker (dev fallback)

Нужны Python 3.12+, Node 20+, опционально Postgres/Redis.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# в .env: USE_SQLITE=1 и CELERY_TASK_ALWAYS_EAGER=1
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8000
```

```powershell
cd web
npm install
$env:VITE_API_BASE="http://127.0.0.1:8000"
npm run dev -- --port 43123
```

---

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
