# Дипломный проект Foodgram



## Описание
Проект позволяет делиться кулинарными хитростями и помогает при в закупке в магазинах

## Инфраструктура
Проект развёрнут на базе БД SQLite, после деплоя на сервер проект будет переведён на PostgreSQL

##### Функционал:
###### Рецепты
- Посмотреть рецепты других
- Создать собственные рецепты
- Добавить понравившиеся рецепты в избранное
- Добавить рецепты в список покупок
- Скачать все необходимые ингредиенты из списка покупок
###### AUTH
- Получение JWT-токена в обмен на email и confirmation_code
###### Пользователи
- Получить список всех пользователей
- Создать пользователя
- Получить данные пользователя по id
- Получить данные своей учетной записи

## Установка локально
Клонируем репозиторий на локальную машину:

```
git clone `https://github.com/PahaPoiss/foodgram_project_react.git`
```

1. Установка docker и docker-compose
Инструкция по установке доступна в официальной инструкции

2. Создать файл .env с переменными окружения
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres # Имя базы данных
POSTGRES_USER=postgres # Администратор базы данных
POSTGRES_PASSWORD=postgres # Пароль администратора
DB_HOST=db
DB_PORT=5432

3. Сборка и запуск контейнера
docker-compose up -d --build

4. Миграции
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

5. Сбор статики
docker-compose exec backend python manage.py collectstatic --noinput

6. Создание суперпользователя Django
docker-compose exec backend python manage.py createsuperuser


### Развернутый локально проект

Развернутый проект будет доступен по адресу `http://localhost`


## Развернутый на сервере проект

Развернутый проект будет доступен по адресу позже



