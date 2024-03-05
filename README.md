### Описание:
Проект «Фудграм» — сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

- Возможность просмотра, создания, редактирования и удаления рецептов.
- Просмотр рецептов других пользователей, добавление их в избранное и в список покупок.
- Возможность подписываться на публикации других пользователей.
- Возможность скачать список покупок.
- Для аутентификации используются токены.

Проект доступен по адресу: [https://foodgramforyou.ddns.net/](https://foodgramforyou.ddns.net/)

### Технологии:

**Языки программирования, библиотеки и модули:**

[![Python](https://img.shields.io/badge/Python-3.9.10%20-blue?logo=python)](https://www.python.org/)

**Фреймворк, расширения и библиотеки:**

[![Django](https://img.shields.io/badge/Django-v3.2.3-blue?logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/Django_REST_Framework-v3.12.4-blue?logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)


**Базы данных и инструменты работы с БД:**

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue?logo=PostgreSQL)](https://www.postgresql.org/)

**Веб-стек технологии:**

[![Docker](https://img.shields.io/badge/Docker-25.0.1-blue?logo=docker)](https://www.docker.com/)
[![Gunicorn](https://img.shields.io/badge/gunicorn-20.1.0-blue?logo=gunicorn)](https://gunicorn.org/)
[![NGINX](https://img.shields.io/badge/NGINX-1.19.3-blue?logo=NGINX)](https://nginx.org/ru/)

### Как локально запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Sh1butani/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Перейти в директорию infra:

```
cd infra
```

Создать и наполнить .env файл. Для примера в директории infra находится файл .env.example:

```
touch .env
```

Выполнить команду для сборки и запуска контейнеров:

```
docker compose up -d
```

Выполнить миграции:

```
docker compose exec backend python manage.py migrate
```

Выполнить команду для заполнения БД тестовыми данными:

```
docker compose exec backend python manage.py load_csv
```

Выполнить команду для создания суперюзера:

```
docker compose exec backend python manage.py createsuperuser
```

Готово! Ознакомиться с проектом Вы можете по адресу: http://localhost:7000/


### Импорт базы данных

В катологе backend/data проекта находятся тестовые файлы базы данных. 
Для их импорта в базу данных выполняется команда:
```
python manage.py load_csv
```

### Примеры запросов к API:

Получение cписка рецептов:
GET /api/v1/recipes

Скачать список покупок:
GET /api/v1/recipes/download_shopping_cart/

Добавить рецепт в избранное:
POST /api/v1/recipes/{id}/favorite/

Отписаться от пользователя:
POST /api/v1/users/{id}/subscribe/


Полный перечень запросов вы можете найти в документации к API, доступной после запуска сервера
по адресу: [http://127.0.0.1:7000/api/docs/](http://127.0.0.1:7000/api/docs/)

### Автор:
[David Pilosyan](https://t.me/Shibutani)
