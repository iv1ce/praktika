# praktika — Защищённая веб-платформа

## Запуск
```bash
cd D:\praktika
python -m app.main          # http://127.0.0.1:8000
```

## Стек
- FastAPI + Uvicorn, SQLAlchemy (SQLite / PostgreSQL)
- JWT (python-jose) + bcrypt (passlib)
- SlowAPI (rate limiting), Jinja2 + HTML/JS фронтенд

## Структура
- `app/config.py` — настройки (БД, SECRET_KEY, JWT). Если указан `DB_HOST` — PostgreSQL, иначе SQLite
- `app/database.py` — engine/session, `get_db`
- `app/models/` — User, Task
- `app/schemas.py` — Pydantic схемы
- `app/services/auth.py` — хэширование, создание/декодинг JWT
- `app/middleware/security.py` — `get_current_user`, `require_admin`
- `app/middleware/audit.py` — логгирование запросов в audit.log
- `app/routes/auth.py` — регистрация, логин
- `app/routes/users.py` — /me, список, удаление (admin)
- `app/routes/tasks.py` — CRUD задач (user видит только свои, admin — все)

## Что сделано
- [x] Регистрация + сообщение об успехе → переход на логин
- [x] Аутентификация по JWT (sub теперь string)
- [x] RBAC (user/admin)
- [x] CRUD задач (API + фронтенд)
- [x] Аудит (audit.log), Rate limiting
- [x] Починены: Jinja2+Starlette несовместимость, passlib+bcrypt, JWT sub тип, редиректы слешей
- [x] PostgreSQL/SQLite переключение через DB_HOST в .env
- [ ] Документация API
- [ ] Руководство пользователя
- [ ] Тесты

## Зависимости
`pip install -r requirements.txt`

## .env пример
```
DB_HOST=localhost    # если не указан — SQLite
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=pass
DB_NAME=praktika
SECRET_KEY=...
```
