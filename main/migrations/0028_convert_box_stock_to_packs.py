from django.db import migrations


def convert_box_counts_to_packs(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    products = Product.objects.using(database).filter(
        sale_unit='piece',
        box_pack_count__gt=1,
        stock_quantity__isnull=False,
    )
    for product in products.iterator():
        product.stock_quantity *= product.box_pack_count
        product.save(using=database, update_fields=['stock_quantity'])


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0027_use_shared_pack_inventory'),
    ]

    operations = [
        migrations.RunPython(convert_box_counts_to_packs, migrations.RunPython.noop),
    ]
