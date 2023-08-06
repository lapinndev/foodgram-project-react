## https://lapinfoodgram.hopto.org/
## admin@yandex.ru | admin

### Foodgram
Продуктовый помощник - сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд

### Технологии
- Python 3.9
- Django 3.2.1
- Nginx
- Docker
- Postgres

### Запуск проекта на локальной машине:

- Клонировать репозиторий:
```
https://github.com/mikhailsoldatkin/foodgram-project-react.git
```

- В директории infra файл example.env переименовать в .env и заполнить своими данными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
```

- Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, 
созданию суперпользователя, как указано выше.
```
docker-compose -f docker-compose-local.yml up -d
```


- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)


- Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)


# Разработчики
- Лапин Максим Романович
