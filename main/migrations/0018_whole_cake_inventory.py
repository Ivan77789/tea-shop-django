from django.db import migrations, models


def split_tea_stock(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    Category = apps.get_model('main', 'Category')
    database = schema_editor.connection.alias
    puer_category_ids = list(
        Category.objects.using(database)
        .filter(name__iexact='Пуэр')
        .values_list('id', flat=True)
    )
    for product in Product.objects.using(database).filter(
        sale_unit='gram', category_id__in=puer_category_ids
    ).iterator():
        raw_weight = (product.weight or '').strip()
        if not raw_weight.isdigit():
            continue
        cake_weight = int(raw_weight)
        if cake_weight <= 0:
            continue
        grams = product.stock_quantity or 0
        product.whole_cake_weight_grams = cake_weight
        product.whole_cake_stock = grams // cake_weight
        product.stock_quantity = grams % cake_weight
        product.save(using=database, update_fields=[
            'whole_cake_weight_grams', 'whole_cake_stock', 'stock_quantity'
        ])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_seed_demo_inventory'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='whole_cake_weight_grams',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Вес целого блина, г', help_text='Если товар можно купить целым блином, укажи его вес в граммах.'),
        ),
        migrations.AddField(
            model_name='product',
            name='whole_cake_stock',
            field=models.PositiveIntegerField(default=0, verbose_name='Целых блинов на складе'),
        ),
        migrations.AddField(
            model_name='product',
            name='whole_cake_discount_percent',
            field=models.PositiveSmallIntegerField(default=21, verbose_name='Скидка на целый блин, %', help_text='Применяется к цене целого блина, рассчитанной из цены за 50 г.'),
        ),
        migrations.RunPython(split_tea_stock, migrations.RunPython.noop),
    ]
