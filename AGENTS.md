# praktika — Защищённая веб-платформа

## Запуск
```bash
cd C:\Users\bosbe\Downloads\praktika
.\venv\Scripts\activate
python -m app.main          # http://127.0.0.1:8000
```

## Стек
- FastAPI + Uvicorn, SQLAlchemy (SQLite / PostgreSQL)
- JWT (python-jose) + bcrypt (passlib)
- SlowAPI (rate limiting), Jinja2 + HTML/JS фронтенд

## Структура
- `app/config.py` — настройки (БД, SECRET_KEY, JWT). Если указан `DB_HOST` — PostgreSQL, иначе SQLite
- `app/database.py` — engine/session, `get_db` (rollback при ошибках)
- `app/limiter.py` — общий Limiter для rate limiting
- `app/models/` — User, Task
- `app/schemas.py` — Pydantic схемы
- `app/services/auth.py` — хэширование (bcrypt), создание/декодинг JWT
- `app/middleware/security.py` — `get_current_user`, `require_admin`
- `app/middleware/audit.py` — аудит в audit.log (USER, IP, METHOD, PATH, STATUS)
- `app/routes/auth.py` — регистрация, логин
- `app/routes/users.py` — CRUD пользователей + админ-функции
- `app/routes/tasks.py` — CRUD задач (user видит свои, admin — все)
- `app/templates/index.html` — фронтенд
- `app/static/app.js` — клиентская логика
- `app/static/style.css` — стили

## Что сделано

### Основные функции
- [x] Регистрация + логин по JWT (проверка is_active при входе)
- [x] RBAC (user/admin): user — свои задачи, admin — все + управление пользователями
- [x] CRUD задач (API + фронтенд)
- [x] Редактирование задачи (название, описание) через кнопку «Редактировать» на фронтенде
- [x] CRUD пользователей (admin): список, удаление, блокировка, смена роли
- [x] Обновление профиля (email, пароль с подтверждением старого)

### Безопасность
- [x] Пароли bcrypt (passlib)
- [x] JWT-токены с expiry (HS256, 60 мин)
- [x] RBAC (user/admin) — проверка на каждом эндпоинте
- [x] Rate limiting (SlowAPI) на каждый эндпоинт
- [x] Brute-force lockout: 5 неудачных → блок 15 мин (423 Locked)
- [x] Security headers: CSP, X-Frame-Options: DENY, HSTS, X-Content-Type-Options: nosniff
- [x] Self-demote защита: admin не может снять себе роль
- [x] Self-block защита: admin не может заблокировать себя
- [x] Сброс brute-force счётчика при разблокировке админом
- [x] Поле locked_until в UserResponse (видно админу)
- [x] Аудит запросов в audit.log (USER, IP, METHOD, PATH, STATUS)
- [x] Global exception handler (500 → JSON, лог ошибки)
- [x] Rollback БД при ошибках
- [x] Защита от SQL-инъекций (SQLAlchemy ORM)
- [x] Защита от XSS (CSP + экранирование на фронтенде)
- [x] Валидация username (regex), email (EmailStr), password (мин 8)
- [x] Авто-миграция новых колонок БД при запуске
- [x] quote_plus для пароля БД (спецсимволы)
- [x] CSP без unsafe-inline для скриптов (все onclick вынесены в JS)

### Инфраструктура
- [x] PostgreSQL/SQLite переключение через DB_HOST в .env
- [x] REST API с JSON
- [x] Авто-документация Swagger (/docs) + ReDoc (/redoc)
- [x] Кнопка API Docs в навигации на сайте

### Прочее
- [x] Удалён мусор (src/main.py, __pycache__)
- [x] Анимации кнопок (hover glow, click scale, loading spinner, fadeSlideIn)
- [x] Сортировка задач: новые сверху (ORDER BY updated_at DESC)
- [x] Поле last_login у пользователя (отображается в админке)
- [x] Обработка ошибок в handleTaskSubmit (показывает под формой)
- [x] Документация API (summary, description во всех эндпоинтах → Swagger)
- [x] Руководство пользователя (GUIDE.md)
- [ ] Тесты

## Rate limits
| Эндпоинт | Лимит |
|----------|-------|
| POST /api/auth/register | 10/min |
| POST /api/auth/login | 20/min |
| GET /api/users/me | 60/min |
| PUT /api/users/me | 10/min |
| GET /api/users | 30/min |
| PATCH /api/users/*/status | 30/min |
| PATCH /api/users/*/role | 30/min |
| DELETE /api/users/* | 30/min |
| GET /api/tasks | 60/min |
| POST /api/tasks | 30/min |
| GET /api/tasks/* | 60/min |
| PUT /api/tasks/* | 30/min |
| DELETE /api/tasks/* | 30/min |

## Зависимости
`pip install -r requirements.txt`

## .env пример
```
DB_HOST=localhost    # если не указан — SQLite
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=
DB_NAME=praktika
SECRET_KEY=...
```
