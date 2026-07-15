# SSS Registry

Внутренний реестр опасных производственных объектов (ОПО), контрагентов, документов и оборудования.

## Стек

- Python 3, Django 6.0.5
- PostgreSQL (psycopg 3)
- Bootstrap 5 + Bootstrap Icons
- gunicorn + nginx (production)

## Возможности

- Учёт объектов (ОПО), контрагентов, оборудования, документов и их вложений
- Календарь поверок оборудования с предупреждениями о приближающихся сроках
- Глобальный поиск по всем разделам
- Ролевая модель доступа:
  - **Админ** (суперпользователь) — полный доступ, включая удаление
  - **Сотрудники** (группа) — создание и редактирование без права удаления
  - **Гость** — только просмотр

## Локальный запуск

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

Создайте базу PostgreSQL и настройте переменные окружения (см. `deploy/.env.example`):

```
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=sss_db
DB_USER=postgres
DB_PASSWORD=...
DB_HOST=127.0.0.1
DB_PORT=5432
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Деплой на сервер

В `deploy/` — шаблоны конфигурации для продакшена:

- `sss.service` — systemd-юнит для gunicorn
- `nginx.conf` — конфигурация nginx (проксирование в gunicorn, отдача `/static/` и `/media/`)
- `.env.example` — список необходимых переменных окружения

Общая схема: клонировать репозиторий, создать venv и БД, задать `.env`, накатить миграции, собрать статику (`collectstatic`), подключить systemd-юнит и nginx.

## Права доступа

Роль пользователя определяется через встроенные группы Django:

- суперпользователь — доступен весь функционал;
- участник группы **«Сотрудники»** — может создавать и редактировать записи, но не удалять;
- любой другой авторизованный пользователь — доступен только просмотр.
