# Фикстуры каталога

`main/category.json` содержит категории из текущей базы данных.
`main/products.json` содержит товары, галереи товаров и дополнительные характеристики.
Пользователи, заказы, избранное и персональные данные в эти файлы не включены.

Чтобы загрузить каталог в пустую базу данных из корня проекта:

```powershell
python manage.py loaddata fixtures/main/category.json fixtures/main/products.json
```

Фикстуры хранят ссылки на изображения, но не сами изображения. Для отображения каталога
скопируйте соответствующие файлы из `media/` вместе с данными.

Обновить фикстуры из активной базы данных:

```powershell
python manage.py dumpdata main.category --indent 2 --output fixtures/main/category.json
python manage.py dumpdata main.product main.productimage main.extraattribute --indent 2 --output fixtures/main/products.json
```
