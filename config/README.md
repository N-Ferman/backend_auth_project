# Custom Auth and Authorization Backend

## Описание

Проект реализует собственную систему аутентификации и авторизации.

Используются:
- собственная таблица users;
- bcrypt для хранения паролей;
- собственная таблица sessions;
- JWT для идентификации пользователя;
- собственные таблицы ролей и правил доступа.

## Схема БД

### users

Хранит пользователей.

Поля:
- id
- email
- password_hash
- last_name
- first_name
- patronymic
- is_active
- created_at
- updated_at
- deleted_at

### sessions

Хранит сессии пользователей.

Поля:
- id
- user_id
- token_jti
- is_active
- created_at
- expires_at
- user_agent
- ip_address

### roles

Хранит роли пользователей.

Примеры:
- admin
- manager
- user
- guest

### user_roles

Связывает пользователей и роли.

### business_elements

Хранит элементы бизнес-приложения:
- users
- access_rules
- products
- orders
- stores

### access_role_rules

Хранит правила доступа роли к элементу.

Права:
- read_permission
- read_all_permission
- create_permission
- update_permission
- update_all_permission
- delete_permission
- delete_all_permission

## Как работает аутентификация

1. Пользователь отправляет email и password.
2. Backend ищет пользователя в users.
3. Backend проверяет password через bcrypt.
4. Backend создаёт запись в sessions.
5. Backend создаёт JWT.
6. Клиент отправляет JWT в заголовке Authorization.
7. Middleware проверяет JWT, session и user.is_active.
8. Если всё хорошо, пользователь записывается в request.auth_user.

## Как работает авторизация

Используется RBAC + ownership.

RBAC — доступ через роли.

Ownership — доступ к своим объектам.

Если пользователь не определён, возвращается 401.
Если пользователь определён, но прав нет, возвращается 403.

## Тестовые пользователи

| Email | Password | Role |
|---|---|---|
| admin@example.com | Admin12345! | admin |
| manager@example.com | Manager12345! | manager |
| user@example.com | User12345! | user |
| guest@example.com | Guest12345! | guest |

## Запуск

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver