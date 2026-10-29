import hashlib

from django.db import migrations, models


RESIN_NAME = 'смола шу пуэра'


def seed_demo_inventory(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias

    for product in Product.objects.using(database).all().iterator():
        seed = hashlib.sha256(f'{product.pk}:{product.slug}'.encode('utf-8')).digest()
        value = int.from_bytes(seed[:4], 'big')

        if product.name.strip().casefold() == RESIN_NAME:
            product.sale_unit = 'piece'
            product.stock_quantity = 8 + (value % 34)
        else:
            product.sale_unit = 'gram'
            # 500 g to 6 kg, in 50 g increments, as demo stock for loose tea.
            product.stock_quantity = (10 + (value % 111)) * 50

        product.save(using=database, update_fields=['sale_unit', 'stock_quantity'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_product_inventory'),
    ]

    operations = [
        migrations.RunPython(seed_demo_inventory, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='product',
            name='sale_unit',
            field=models.CharField(
                choices=[('piece', 'Поштучно'), ('gram', 'На развес, граммы')],
                default='gram',
                max_length=10,
                verbose_name='Единица продажи',
            ),
        ),
    ]
