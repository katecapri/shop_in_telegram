<h1 align="center">Магазин в телеграме с админ-панелью Django</h1>

 ![](https://github.com/katecapri/images-for-readme/blob/main/256.png) ![](https://github.com/katecapri/images-for-readme/blob/main/django.png) ![](https://github.com/katecapri/images-for-readme/blob/main/docker.png)

 
##  Описание ##

В проекте реализована авторизация, получение категорий продуктов, подкатегорий и товаров в подкатегориях с пагинацией. Реализована корзина, из которой можно оформить заказ , получить ссылку на оплату, после чего информация о 
клиенте и состав с суммой заказа становятся доступны администратору в Excel-файле на локальном компьютере. Карточки товаров, категории, просмотр клиентов, продуктовых корзин клиентов реализован через админку Django.

##  Используемые технологии ##

- Python
- Django
- Aiogram
- Pillow
- Postgres
- Asyncpg
- Pylint
- Yookassa
- Openpyxl

##  Инструкция по развертыванию ##

1. В файле окружения в корневой директории задать значение переменным SHOP_BOT_TELEGRAM_TOKEN.
2. В корневой директории ввести команду:

> make run


##  Результат ##

По адресу http://0.0.0.0:8008/admin можно сразу войти в админку по логину и паролю admin / admin (преднастроено в скрипте запуска). Заполняются категории и карточки товаров. 

![](https://github.com/katecapri/images-for-readme/blob/main/1_шоп.jpg)

После этого в телеграм-боте осуществляется короткая регистрация, выбираются товары из каталога, оформляется корзина.
![](https://github.com/katecapri/images-for-readme/blob/main/2_шоп.jpg) 
![](https://github.com/katecapri/images-for-readme/blob/main/3_шоп.jpg)
![](https://github.com/katecapri/images-for-readme/blob/main/4_шоп.jpg)
