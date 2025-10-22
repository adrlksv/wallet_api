# Wallet API

REST API для управления кошельками и операциями с балансом.

## Стек

- FastAPI + SQLAlchemy (async)
- PostgreSQL 17
- Docker + docker-compose
- Alembic (миграции)
- Pytest (тесты)

## Быстрый старт

### 1. Создать `.env` файл

```env
# PostgreSQL
POSTGRES_DB=wallet_db
POSTGRES_USER=wallet_user
POSTGRES_PASSWORD=wallet_password
TEST_DB_NAME=wallet_db_test

# Application
APP_CONFIG__DB__SCHEME=postgresql+asyncpg
APP_CONFIG__DB__HOST=db
APP_CONFIG__DB__PORT=5432
APP_CONFIG__DB__USER=wallet_user
APP_CONFIG__DB__PASSWORD=wallet_password
APP_CONFIG__DB__NAME=wallet_db
APP_CONFIG__DB__ECHO=false
APP_CONFIG__DB__ECHO_POOL=false
APP_CONFIG__DB__POOL_SIZE=50
APP_CONFIG__DB__MAX_OVERFLOW=10
APP_CONFIG__TEST_DB_NAME=wallet_db_test
```

### 2. Запустить проект

```bash
docker compose up -d
```

API доступен на `http://localhost:8000`

Swagger документация: `http://localhost:8000/api/docs`

## API Endpoints

### Создать кошелек
```bash
curl -X POST http://localhost:8000/api/wallets/create_wallet
```
Ответ:
```json
{
  "wallet_id": "uuid",
  "balance": "0.0",
  "created_at": "2025-10-22T10:00:00"
}
```

### Получить кошелек
```bash
curl http://localhost:8000/api/wallets/{wallet_uuid}
```

### Получить все кошельки
```bash
curl "http://localhost:8000/api/wallets/get_wallets?skip=0&limit=100"
```

### Пополнить кошелек
```bash
curl -X POST http://localhost:8000/api/wallets/{wallet_uuid}/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "DEPOSIT", "amount": "100.50"}'
```

### Снять с кошелька
```bash
curl -X POST http://localhost:8000/api/wallets/{wallet_uuid}/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "WITHDRAW", "amount": "50.00"}'
```

## Тесты

### Что тестируется

**Repository Layer (13 тестов):**
- CRUD операции с кошельками
- Пополнение/снятие средств
- Валидация недостаточного баланса
- Edge cases (большие суммы, точность Decimal)

**API Endpoints (19 тестов):**
- Создание кошельков
- Получение кошельков (один/список/пагинация)
- Операции DEPOSIT/WITHDRAW
- Валидация входных данных
- Обработка ошибок (404, 400, 422)
- Конкурентные операции

### Запуск тестов

Перед запуском тестов поменять в `.env`:
```env
APP_CONFIG__DB__HOST=localhost
```

Затем:
```bash
# Установить зависимости
poetry install

# Запустить тесты
poetry run pytest

# С покрытием
poetry run pytest --cov=app --cov-report=html
```

После тестов вернуть обратно:
```env
APP_CONFIG__DB__HOST=db
```
