# Система управления персональными финансами

Fullstack-приложение для учёта доходов, расходов и управления личным бюджетом.

## Стек технологий

| Слой       | Технология          |
|------------|---------------------|
| Backend    | Python, FastAPI      |
| Frontend   | React, Vite          |
| База данных| PostgreSQL           |
| Контейнеры | Docker, Docker Compose |

## Структура проекта

```
personal-finance-system/
├── backend/          # REST API на FastAPI
├── frontend/         # SPA на React + Vite
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Возможности (планируемые)

- Учёт доходов и расходов по категориям
- Управление несколькими счетами / кошельками
- Аналитика и графики по периодам
- Бюджетирование и лимиты по категориям
- Экспорт данных

## Запуск

```bash
# Запуск через Docker Compose
docker compose up --build

# Backend (dev)
cd backend
uvicorn app.main:app --reload

# Frontend (dev)
cd frontend
npm install && npm run dev
```

## Лицензия

MIT
