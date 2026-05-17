# Система управления персональными финансами

Fullstack клиент-серверное приложение для учёта личных финансов.
Позволяет вести учёт доходов и расходов, управлять счетами,
категоризировать транзакции и анализировать финансовое состояние.

---

## Технологический стек

| Слой | Технология | Версия |
|---|---|---|
| Backend | FastAPI | 0.115 |
| ORM | SQLAlchemy | 2.0 |
| База данных | PostgreSQL | 16 |
| Миграции | Alembic | 1.14 |
| Аутентификация | JWT (python-jose) | — |
| Frontend | React | 18 |
| Сборщик | Vite | 6 |
| Стили | Tailwind CSS | 3 |
| Состояние | Zustand | — |
| Графики | Recharts | — |
| Тестирование | pytest + pytest-asyncio + httpx | — |
| Фаззинг | Hypothesis | 6.112 |
| Инфраструктура | Docker + Docker Compose | — |

---

## Архитектура

```
┌─────────────────────┐        HTTP/REST + JWT        ┌─────────────────────┐
│   Frontend (React)  │ ──────────────────────────▶  │  Backend (FastAPI)  │
│   SPA · порт 5173   │ ◀──────────────────────────  │   REST API · 8000   │
└─────────────────────┘                               └──────────┬──────────┘
                                                                 │ SQLAlchemy async
                                                      ┌──────────▼──────────┐
                                                      │  PostgreSQL 16       │
                                                      │  порт 5432           │
                                                      └─────────────────────┘
```

- **Frontend** — React SPA, общается с бэкендом через `axios`. Zustand хранит состояние авторизации и уведомлений. Recharts строит графики.
- **Backend** — FastAPI с async-эндпоинтами, JWT-аутентификация, Pydantic-валидация запросов/ответов.
- **БД** — PostgreSQL 16; схема управляется Alembic-миграциями, ORM — SQLAlchemy 2.0 Mapped API.

---

## Функциональность

| Раздел | Возможности |
|---|---|
| Авторизация | Регистрация, вход, JWT-токен, смена пароля, обновление профиля |
| Счета | Создание (наличные / карта / накопления), редактирование, удаление |
| Транзакции | Доходы / расходы / переводы, фильтры, пагинация, обновление баланса счёта |
| Категории | Пользовательские + системные, цвет и emoji-иконка, два типа (доход/расход) |
| Аналитика | PieChart расходов по категориям, BarChart доходов/расходов, выбор периода |
| Дашборд | Общий баланс, доходы/расходы за месяц, список счетов, последние транзакции |
| Профиль | Редактирование имени, смена пароля, статистика (счета, транзакции, дата регистрации) |

---

## Быстрый старт

### Docker Compose (рекомендуется)

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd personal-finance-system

# 2. Создать файл переменных окружения
cp .env.example .env

# 3. Запустить всё одной командой
docker compose up --build -d
```

Откройте **http://localhost:5173**

> Миграции применяются автоматически при старте backend-контейнера.

### Тестовые данные

```bash
docker exec -it personal-finance-system-backend-1 python seed_data.py
```

| Email | Пароль | Роль |
|---|---|---|
| admin@finance.app | admin123 | Администратор |
| user@finance.app | user123 | Пользователь |

---

## Локальная разработка без Docker

### Backend

```bash
cd backend

# Создать и активировать виртуальное окружение
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Скопировать и настроить переменные окружения
cp .env.example .env   # при необходимости отредактировать

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

API доступно на **http://localhost:8000**

### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Скопировать переменные окружения
cp .env.example .env.local

# Запустить dev-сервер
npm run dev
```

Приложение откроется на **http://localhost:5173**

---

## Тестирование

```bash
cd backend

# Все тесты с отчётом о покрытии
pytest --cov=app --cov-report=term-missing

# HTML-отчёт о покрытии
pytest --cov=app --cov-report=html

# Только фаззинг-тесты
pytest tests/test_fuzz.py -v
```

Тестовый стек: **35 unit-тестов** (pytest-asyncio + SQLite in-memory) + **6 фаззинг-тестов** (Hypothesis, 50 примеров каждый).

---

## API документация

| URL | Описание |
|---|---|
| http://localhost:8000/docs | Swagger UI (интерактивный) |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Healthcheck |

### Основные эндпоинты

```
POST   /api/v1/auth/register          — регистрация
POST   /api/v1/auth/token             — получить JWT
GET    /api/v1/auth/me                — профиль текущего пользователя
PATCH  /api/v1/auth/me                — обновить имя
POST   /api/v1/auth/change-password   — сменить пароль

GET    /api/v1/accounts/              — список счетов
POST   /api/v1/accounts/              — создать счёт
PUT    /api/v1/accounts/{id}          — обновить счёт
DELETE /api/v1/accounts/{id}          — удалить счёт

GET    /api/v1/transactions/          — список транзакций (с фильтрами)
POST   /api/v1/transactions/          — создать транзакцию
PUT    /api/v1/transactions/{id}      — обновить транзакцию
DELETE /api/v1/transactions/{id}      — удалить транзакцию
GET    /api/v1/transactions/analytics — аналитика за период

GET    /api/v1/categories/            — список категорий
POST   /api/v1/categories/            — создать категорию
DELETE /api/v1/categories/{id}        — удалить категорию
```

---

## Структура проекта

```
personal-finance-system/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy модели (User, Account, Category, Transaction)
│   │   ├── schemas/         # Pydantic схемы запросов и ответов
│   │   ├── routers/         # FastAPI роутеры (auth, accounts, categories, transactions)
│   │   └── services/        # Бизнес-логика (CRUD, аналитика, JWT)
│   ├── alembic/
│   │   └── versions/        # Миграции БД
│   ├── tests/               # 35 unit-тестов + 6 фаззинг-тестов
│   ├── seed_data.py         # Скрипт тестовых данных
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
├── frontend/
│   └── src/
│       ├── api/             # axios-клиент и функции для каждого ресурса
│       ├── components/      # Переиспользуемые компоненты (Button, Input, Modal, Toast…)
│       ├── pages/           # Страницы (Dashboard, Accounts, Transactions, Analytics…)
│       ├── store/           # Zustand: authStore, toastStore
│       └── utils/           # formatters.js, validators.js
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Переменные окружения

### Корневой `.env` (для Docker Compose)

| Переменная | По умолчанию | Описание |
|---|---|---|
| `POSTGRES_USER` | postgres | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | postgres | Пароль PostgreSQL |
| `POSTGRES_DB` | finance | Имя базы данных |
| `SECRET_KEY` | — | Секрет для подписи JWT (**обязательно сменить**) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Время жизни токена |

### `backend/.env` (локальная разработка)

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/finance
SECRET_KEY=super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
```

### `frontend/.env.local`

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Лицензия

MIT
