# Task Manager API — Облачный сервис управления задачами

Курсовой проект по дисциплине «Интеграция и управление приложениями на удалённом сервере»
Тема: "Разработка облачного сервиса управления задачами с контролем выполнения"

**Студент:** Степанова Мария Алексеевна  
**Кафедра:** Прикладной информатики и информационной безопасности  
**Университет:** РЭУ им. Г.В. Плеханова, 2026



## О проекте

REST API для облачного сервиса управления задачами с контролем выполнения. Реализован по архитектурному паттерну **Backend-for-Frontend (BfF)** — единый API обслуживает веб-клиент (React), мобильное приложение (Flutter) и любые внешние интеграции.

Авторизованные пользователи могут создавать задачи, устанавливать дедлайны и приоритеты, отмечать выполнение и просматривать статистику. Администраторы управляют всеми пользователями и задачами системы.



## Стек технологий

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.10 |
| Фреймворк | Django 4.2 LTS |
| REST API | Django REST Framework 3.14 |
| Аутентификация | JWT (djangorestframework-simplejwt 5.3) |
| База данных | PostgreSQL 15 |
| Кэширование | Redis 7 |
| Веб-сервер | Nginx + Gunicorn |
| Контейнеризация | Docker / Docker Compose |



## Быстрый старт

### Требования

- Docker Desktop (версия 24.0+)
- Docker Compose (версия 2.20+)

### Запуск

```bash
# 1. Перейти в папку с проектом
cd taskmanager_backend

# 2. Создать файл с переменными окружения
cp .env.example .env

# 3. Открыть .env и установить свои значения
#    SECRET_KEY, DB_PASSWORD — обязательно поменять

# 4. Собрать и запустить все контейнеры
docker-compose up --build
```

Дождитесь строки в консоли:
```
==> Starting Gunicorn...
```

### Создать администратора (в отдельном терминале)

```bash
docker-compose exec web python manage.py createsuperuser
```

### Адреса после запуска

| Что | Адрес |
|-----|-------|
| API | http://localhost:8080 |
| Административная панель | http://localhost:8080/admin |

---

## Структура проекта

```
taskmanager_backend/
├── taskmanager_backend/     # Настройки Django-проекта
│   ├── settings.py          # Конфигурация (БД, JWT, CORS, кэш)
│   ├── urls.py              # Корневые URL-маршруты
│   └── wsgi.py
├── users/                   # Приложение: пользователи и аутентификация
│   ├── models.py            # CustomUser (AbstractUser + email + phone)
│   ├── serializers.py       # UserRegistrationSerializer, UserSerializer
│   ├── views.py             # RegisterView, UserManagementViewSet
│   ├── urls.py              # Маршруты auth/
│   └── admin.py             # Настройки отображения в AdminPanel
├── tasks/                   # Приложение: задачи и отметки выполнения
│   ├── models.py            # Task, TaskCompletion
│   ├── serializers.py       # TaskSerializer, StatisticsSerializer
│   ├── views.py             # TaskViewSet, CompletionViewSet, StatisticsAPIView
│   ├── urls.py              # Маршруты tasks/
│   ├── permissions.py       # IsOwnerOrAdmin
│   └── admin.py             # Настройки отображения в AdminPanel
├── entrypoint.sh            # Скрипт запуска (makemigrations→migrate→gunicorn)
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── requirements.txt
└── .env.example
```

---

## API Endpoints

### Аутентификация (не требует токена)

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/api/auth/register/` | Регистрация нового пользователя |
| `POST` | `/api/auth/token/` | Получение Access + Refresh токенов |
| `POST` | `/api/auth/token/refresh/` | Обновление Access-токена |

### Задачи (требует токен)

| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/api/tasks/` | Список задач текущего пользователя |
| `POST` | `/api/tasks/` | Создание новой задачи |
| `GET` | `/api/tasks/{id}/` | Детали задачи с отметками выполнения |
| `PUT` | `/api/tasks/{id}/` | Полное обновление задачи |
| `PATCH` | `/api/tasks/{id}/` | Частичное обновление задачи |
| `DELETE` | `/api/tasks/{id}/` | Удаление задачи |
| `GET` | `/api/tasks/{id}/completions/` | Список отметок выполнения |
| `POST` | `/api/tasks/{id}/completions/` | Отметить задачу выполненной |
| `GET` | `/api/tasks/statistics/` | Статистика по задачам пользователя |

### Администрирование (требует is_staff=True)

| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/api/auth/admin/users/` | Список всех пользователей системы |
| `PUT` | `/api/auth/admin/users/{id}/` | Изменение учётной записи |
| `DELETE` | `/api/auth/admin/users/{id}/` | Удаление пользователя |

---

## Примеры запросов

### Регистрация

```bash
curl -X POST http://localhost:8080/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "email": "maria@example.com",
    "password": "Secure123!",
    "password_confirm": "Secure123!"
  }'
```

Ответ `201 Created`:
```json
{
  "id": 2,
  "username": "maria",
  "email": "maria@example.com",
  "phone": null,
  "is_staff": false,
  "is_active": true,
  "created_at": "2026-05-21T15:00:00+03:00"
}
```

### Получение JWT-токена

```bash
curl -X POST http://localhost:8080/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "maria@example.com", "password": "Secure123!"}'
```

Ответ `200 OK`:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Создание задачи

```bash
curl -X POST http://localhost:8080/api/tasks/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Подготовить отчёт",
    "description": "Ежемесячный отчёт по отделу",
    "deadline": "2026-06-01T18:00:00+03:00",
    "priority": "high"
  }'
```

Ответ `201 Created`:
```json
{
  "id": 1,
  "title": "Подготовить отчёт",
  "status": "pending",
  "priority": "high",
  "deadline": "2026-06-01T18:00:00+03:00",
  "is_overdue": false,
  "completions": []
}
```

### Статистика

```bash
curl -X GET http://localhost:8080/api/tasks/statistics/ \
  -H "Authorization: Bearer <access_token>"
```

Ответ `200 OK`:
```json
{
  "total": 5,
  "completed": 3,
  "overdue": 1,
  "pending": 1,
  "completion_rate": 60.0
}
```

---

## Безопасность

- Аутентификация через **JWT** (RFC 7519, HMAC-SHA256)
- **Access-токен** — время жизни 60 минут
- **Refresh-токен** — время жизни 1 день, инвалидируется после использования
- Пользователь видит **только свои задачи** — фильтрация на уровне queryset
- Пароли хранятся в виде хэша **PBKDF2+SHA256**
- Неавторизованные запросы → **401 Unauthorized**
- Запросы без прав администратора к admin-эндпоинтам → **403 Forbidden**

---

## Управление контейнерами

```bash
# Запустить
docker-compose up --build

# Остановить
docker-compose down

# Посмотреть статус контейнеров
docker-compose ps

# Посмотреть логи веб-приложения
docker-compose logs web

# Открыть консоль Django
docker-compose exec web python manage.py shell
```

---

## Модели данных

### CustomUser
| Поле | Тип | Описание |
|------|-----|----------|
| id | BigInt | Первичный ключ |
| email | VARCHAR(254) | Уникальный, используется как логин |
| username | VARCHAR(150) | Имя пользователя |
| phone | VARCHAR(20) | Номер телефона (опционально) |
| is_staff | Boolean | Флаг администратора |
| is_active | Boolean | Активность учётной записи |

### Task
| Поле | Тип | Описание |
|------|-----|----------|
| id | BigInt | Первичный ключ |
| owner | FK → User | Владелец задачи |
| title | VARCHAR(255) | Заголовок |
| description | Text | Описание |
| deadline | DateTime | Дедлайн (опционально) |
| status | VARCHAR | pending / completed / overdue |
| priority | VARCHAR | low / medium / high |

### TaskCompletion
| Поле | Тип | Описание |
|------|-----|----------|
| id | BigInt | Первичный ключ |
| task | FK → Task | Связанная задача (CASCADE) |
| completed_at | DateTime | Дата и время отметки |
| comment | Text | Комментарий (опционально) |
