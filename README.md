# Практика ИБС — Защищённая веб-платформа

Летняя лабораторная практика. Веб-платформа с управлением задачами, ролевой моделью и REST API.

## Быстрый старт

```bash
pip install -r requirements.txt
python setup.py          # настройка БД (PostgreSQL или SQLite)
python -m app.main       # http://127.0.0.1:8000
```

## Возможности

- Регистрация и аутентификация по JWT
- Две роли: `user` (свои задачи) и `admin` (все задачи + управление пользователями)
- CRUD задач
- Управление профилем (email, пароль)
- Админ-панель: список пользователей, блокировка, смена роли, удаление
- Rate limiting на каждый эндпоинт
- Аудит запросов (audit.log)
- Документация API: `/docs` (Swagger) и `/redoc` (ReDoc)

## Технологии

- **Бэкенд:** FastAPI + Uvicorn, SQLAlchemy, Pydantic
- **БД:** PostgreSQL или SQLite (переключение через .env)
- **Аутентификация:** JWT (python-jose) + bcrypt (passlib)
- **Безопасность:** SlowAPI, защита от SQL-инъекций (ORM), XSS (экранирование)
- **Фронтенд:** Jinja2, HTML, CSS, JavaScript

## Структура

```
praktika/
├── app/
│   ├── main.py              # точка входа
│   ├── config.py            # настройки (БД, JWT, SECRET_KEY)
│   ├── database.py          # подключение к БД
│   ├── limiter.py           # rate limiter
│   ├── schemas.py           # Pydantic схемы
│   ├── models/              # SQLAlchemy модели (User, Task)
│   ├── routes/              # эндпоинты (auth, users, tasks)
│   ├── middleware/          # аудит + проверка JWT/ролей
│   ├── services/            # хэширование, JWT
│   ├── templates/           # HTML
│   └── static/              # CSS, JS
├── setup.py                 # интерактивная настройка
└── requirements.txt         # зависимости
```

## API

Полная документация доступна в Swagger после запуска:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/auth/register | Регистрация |
| POST | /api/auth/login | Вход |
| GET | /api/users/me | Профиль |
| PUT | /api/users/me | Обновление профиля |
| GET | /api/users | Список пользователей (admin) |
| PATCH | /api/users/{id}/status | Блокировка/разблокировка (admin) |
| PATCH | /api/users/{id}/role | Смена роли (admin) |
| DELETE | /api/users/{id} | Удаление пользователя (admin) |
| GET | /api/tasks | Список задач |
| POST | /api/tasks | Создать задачу |
| GET | /api/tasks/{id} | Просмотр задачи |
| PUT | /api/tasks/{id} | Редактировать задачу |
| DELETE | /api/tasks/{id} | Удалить задачу |
