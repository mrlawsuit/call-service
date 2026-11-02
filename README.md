# Call Service

Тестовое задание:
Упрощенная модель интеграционного сервиса. Сервис получает результаты звонков из очереди RabbitMQ, сохраняет их в MongoDB и отдает данные через REST API.

## Требования
- Docker и плагин `docker compose`;
- Python 3.10+ на хосте для запуска `producer.py`;
- `uv` — запускать приложение или тесты локально.

## Зависимости

Зависимости приложения заданы в `pyproject.toml`.
В проекте задан Python 3.12 через `.python-version` (требование задания: Python 3.10+).
`requirements.txt` не используется.

Для локальной разработки с установленным uv:

```bash
uv sync                      # создать .venv и установить основные зависимости
uv run uvicorn src.server:app --reload  # запуск вне Docker, если MongoDB/RabbitMQ доступны. Флаг reload использовать только в dev среде
uv run pytest src/tests/api.py -v            # тесты: API, DI, (не хватает use cases, consumer и repositories) 
```

## Архитектура: Repository → Service → Use Case
Проект разделён по слоям и использует `punq` для реализации DI.

```text

├── api
│   └── v1
│       └── handlers
│           └── campaign.py         # REST API: только вызов use case
├── application
│   ├── services
│   │   ├── calls.py                # операции над звонками
│   │   └── campaigns.py            # операции над кампаниями
│   └── use_cases
│       ├── get_campaign_calls.py   # проверить кампанию → получить звонки
│       └── save_call_event.py      # создать кампанию → сохранить звонок
├── core
│   ├── api
│   │   └── routers.py
│   ├── config.py                   # настройки окружения
│   ├── container.py                # punq: регистрация и сборка зависимостей
│   ├── repositories
│   │   └── base.py             # ABC-контракты репозиториев
│   └── server.py               # lifespan FastAPI и основной источник запуска приложения
├── domain
│   └── models.py                   # Pydantic-модели событий и ответов
├── infrastructure
│   ├── mongodb.py                  # индексы БД
│   ├── rabbitmq.py                 # консюмер
│   └── repositories
│       ├── base.py                 # общий Mongo CRUD-репозиторий
│       ├── calls.py                # upsert звонка и выборка по кампании
│       └── campaigns.py            # upsert кампании
└── tests
    ├── test_api.py
    └── test_di.py  
```

## 1. Запуск

```bash
docker compose up
```

После успешного запуска контейнеров. Во **втором терминале**, из корня репозитория:

```bash
python producer.py
```

Продюсер публикует **4 сообщения** (2 на `camp_001` и 2 на `camp_002`), затем дожидается, пока API подтвердит сохранение всех четырёх звонков. Поэтому сразу после завершения `producer.py` можно проверять результат без задержек.

## 2. Проверка

```bash
curl -s http://localhost:8000/campaigns/camp_001/calls
```

Результат: JSON-массив **ровно из 2 звонков** с `call_id` `call_0001`, `call_0002`. У каждой записи `campaign_id = camp_001`:

```json
[
{
"call_id": "call_0001",
"campaign_id": "camp_001",
"phone": "79001234567",
"status": "success",
"created_at": "2026-10-20T10:06:00Z"
},
{
"call_id": "call_0002",
"campaign_id": "camp_001",
"phone": "79001234568",
"status": "failed",
"created_at": "2026-10-20T10:07:00Z"
}
]
```

Swagger / Pydantic response schema: http://localhost:8000/docs

RabbitMQ Management UI: http://localhost:15672 (`calls_user` / `calls_password`). MongoDB доступна на `127.0.0.1:27017`, база `call_service`, коллекции `campaigns` и `calls`.

## Что не успел
- Добавить unit тестов для покрытия слоев репозиториев, сервисов и т.д.
- Оформить автоматичсескую CI проверку линтеров и прогон тестов, на данный момент можно запусить тесты:
```bash
uv run pytest -v
```
