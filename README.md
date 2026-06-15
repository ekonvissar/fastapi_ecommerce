# fastapi_ecommerce

![Tests](https://github.com/ekonvissar/fastapi_ecommerce/actions/workflows/tests.yml/badge.svg)

Backend интернет-магазина на FastAPI. Учебный проект: async PostgreSQL, Redis, JWT, роли, корзина, заказы, WebSocket при
checkout.

**Стек:** FastAPI · SQLAlchemy 2 (async) · PostgreSQL · Redis · Alembic · pytest

Документация API после запуска: `/docs`

---

## Запуск

Нужен `.env` в корне. Пример:

```env
POSTGRES_DB=ecommerce_db
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=...

DATABASE_URL=postgresql+asyncpg://ecommerce_user:...@db:5432/ecommerce_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=...

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

Без Docker — хост `db` в `DATABASE_URL` меняется на `localhost`.

Для docker-compose ещё нужны dev-сертификаты в `app/cert/` (`localhost.pem`, `localhost-key.pem`). Если их нет:

```bash
mkdir -p app/cert
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout app/cert/localhost-key.pem \
  -out app/cert/localhost.pem \
  -days 365 -subj "/CN=localhost"
```

```bash
docker compose up --build
```

API на **https://localhost:443**

Локально без docker:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Production-вариант: `docker compose -f docker-compose.prod.yml up --build` (gunicorn + nginx).

---

## Что внутри

**Роли:** `buyer`, `seller`, `admin`

**Основные роуты:**

- `/users` — регистрация, логин, refresh/logout
- `/categories`, `/products` — каталог
- `/cart`, `/orders` — корзина и checkout
- `/reviews` — отзывы
- `/ws/orders` — уведомления о заказе (нужен access token в query)

Access token — в заголовке `Authorization: Bearer ...`. Refresh — httpOnly cookie на `/users`, jti в Redis.

Celery в проекте есть, но по сути демо (`app/task.py`), worker в compose не поднимается.

---

## Архитектура

**Modular layered monolith** — один деплой, одна БД, код разбит по доменам и слоям:

```
API (router)  →  Service  →  Repository  →  ORM / PostgreSQL
```

| Модуль           | Что внутри                                        |
|------------------|---------------------------------------------------|
| `identity/`      | пользователи, JWT, refresh в Redis                |
| `catalog/`       | категории, товары, отзывы                         |
| `ordering/`      | корзина, заказы, checkout                         |
| `notifications/` | WebSocket                                         |
| `shared/`        | общие ошибки, exception handlers, схема `Product` |
| `models/`        | SQLAlchemy-модели (общие для всех модулей)        |

Роутеры подключаются явно в `app/router_loader.py`

Доменные ошибки (`CartEmptyError`, `IdentityError`, `CatalogError` и т.д.) всплывают из сервисов и превращаются в
HTTP-ответы в `shared/exception_handlers.py`.

`app/auth.py` — тонкий re-export из `identity/` (чтобы импортировался `get_current_user`).

---

## Тесты

```bash
pytest
pytest -v
pytest --cov=app --cov-report=html   # отчёт в htmlcov/
```

Тесты не требуют postgres/redis — БД и redis подменяются в `tests/conftest.py` (SQLite in-memory + FakeRedis).

Если нет `.env`, перед запуском:

```bash
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export SECRET_KEY="test-secret-key"
export REDIS_URL="redis://localhost:6379/0"
```

В `TestClient` нужен `base_url="http://localhost"` — иначе `TrustedHostMiddleware` отдаст 400.

CI: GitHub Actions на push/PR в `main`, `master`, `additional-features` — см. `.github/workflows/tests.yml`.
