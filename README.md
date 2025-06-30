# ReviewHub

## Описание

ReviewHub - это проект, который позволяет пользователям оставлять отзывы на различные произведения, такие как книги, фильмы и музыка. Пользователи могут оценивать произведения и оставлять комментарии.
<br>

## Стек технологий
**Python** — высокоуровневый язык программирования общего назначения с динамической строгой типизацией и автоматическим управлением памятью.

**Django** — свободный фреймворк для веб-приложений на языке Python, использующий шаблон проектирования MVC.

**Django REST framework (DRF)** — мощный набор инструментов для создания веб-сервисов и API на основе фреймворка Django. 

**SQLite3** — консольная утилита для работы с SQLite. Она запускается и работает в командной строке, в консоли операционной системы.


## Ресурсы ReviewHub

- **auth** ресурс: аутентификация.

- **users** ресурс: пользователи.

- **titles** ресурс: произведения, на которые пишут отзывы (конкретный фильм, книга или песня).

- **categories** ресурс: категории (типы) произведений ("Фильмы", "Книги", "Музыка").

- **genres** ресурс: жанры произведений. Одно произведение может быть связано с несколькими жанрами.

- **reviews** ресурс: отзывы на произведения. Отзыв привязан к конкретному произведению.

- **comments** ресурс: комментарии к отзывам. Комментарий привязан к конкретному отзыву.


## Установка

Для запуска приложения проделайте следующие шаги:

1. Склонируйте репозиторий:
```
git clone https://github.com/bakhvalov4/ReviewHub
```

2. Перейдите в папку с кодом и создайте виртуальное окружение:
```
cd api_yamdb
python -m venv venv
```

3. Активируйте виртуальное окружение:
```
source venv\scripts\activate
```
4. Установите зависимости:
```
python -m pip install -r requirements.txt
```
5. Выполните миграции:
```
python manage.py migrate
```
6. Создайте суперпользователя:
```
python manage.py createsuperuser
```
7. Запустите сервер:
```
python manage.py runserver
```
Проект запущен и доступен по адресу: [localhost:8000](http://localhost:8000/)

## Загрузка данных из csv в БД

Чтобы загрузить таблицы из csv в базу данных:
```
python manage.py load_csv --all
```
Чтобы очистить базу данных: 
```
python manage.py load_csv --clear
```

## Использование

1. Запустите сервер:
    ```
    python manage.py runserver
    ```
2. Откройте браузер и перейдите по адресу:
    ```
    http://127.0.0.1:8000/
    ```

## Документация API

Документация API доступна по адресу:
http://127.0.0.1:8000/redoc/


## Примеры запросов

Пример POST-запроса для регистрации нового пользователя.

*POST .../api/v1/auth/signup/*

```json
{
  "email": "user@no-admin.ru",
  "username": "user"
}
```

Пример ответа:

```json
{
    "email": "user@no-admin.ru",
    "username": "user"
}
```

Пример POST-запроса для получения токена.

*POST .../api/v1/auth/token/*

```json
{
  "username": "user",
  "confirmation_code": "ef2b1eca27544c91e515e31660eb9597"
}
```

Пример ответа:

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5NTE5NzkwLCJqdGkiOiJhYWU0OTI5MjJiYzA0ZjhjOTg0YmYyMmNjZDM3NGU2ZSIsInVzZXJfaWQiOjJ9.r8tNCbSmsNY7abN3HFEI0tRq_ADr10QojJfisIn2H3E"
}
```

Пример GET-запроса для получения списка всех произведений.

*GET .../api/v1/titles/*

Пример ответа:

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 4,
            "name": "Empty genre",
            "year": 2020,
            "rating": null,
            "description": "Test title with empty genre by admin",
            "genre": [],
            "category": null
        }
    ]
}
```

Пример PATCH-запроса для обновления информации о произведении.

*PATCH .../api/v1/titles/4/*

```json
{
    "name": "Empty genre 2",
    "year": 2024,
    "description": "Example of updating product information"
}
```

Пример ответа:

```json
{
    "id": 4,
    "genre": [],
    "category": null,
    "name": "Empty genre 2",
    "rating": 0,
    "year": 2024,
    "description": "Example of updating product information"
}
```


## Авторство
**Авторы:** Бахвалов Н., Мухин В., Лампежев А.<br>
**Контакты:** abas.lampejev@yandex.ru<br>
**Дата создания:** 04.02.2025 г.
