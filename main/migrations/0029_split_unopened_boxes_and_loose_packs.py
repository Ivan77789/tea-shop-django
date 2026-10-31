from django.db import migrations, models


def split_aggregate_pack_stock(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    products = Product.objects.using(database).filter(
        sale_unit='piece',
        stock_quantity__isnull=False,
    )
    for product in products.iterator():
        packs_per_box = max(product.box_pack_count, 1)
        boxes, loose_packs = divmod(product.stock_quantity, packs_per_box)
        product.stock_quantity = boxes
        product.loose_pack_stock = loose_packs
        product.save(using=database, update_fields=['stock_quantity', 'loose_pack_stock'])


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0028_convert_box_stock_to_packs'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='loose_pack_stock',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Отдельные пакетики, оставшиеся после вскрытия коробок. Пробник расходует один пакетик.',
                verbose_name='Пакетиков из вскрытых коробок (шт.)',
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text='Количество целых закрытых коробок. Для развесного чая — остаток в граммах.',
                null=True,
                verbose_name='Нераспечатанных коробок (шт.)',
            ),
        ),
        migrations.RunPython(split_aggregate_pack_stock, migrations.RunPython.noop),
    ]
