from django.db import migrations


def configure_smola_as_portions(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    product = Product.objects.using(database).filter(slug='smola-shu-puera').first()
    if product is None:
        return

    # Preserve the existing number of saleable pieces while expressing stock in grams.
    if product.stock_quantity is not None:
        product.stock_quantity *= 2
    product.sale_unit = 'portion'
    product.portion_weight_grams = 2
    product.save(using=database, update_fields=[
        'sale_unit', 'portion_weight_grams', 'stock_quantity',
    ])


def restore_smola_to_pieces(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    product = Product.objects.using(database).filter(slug='smola-shu-puera').first()
    if product is None:
        return
    if product.stock_quantity is not None:
        product.stock_quantity //= 2
    product.sale_unit = 'piece'
    product.portion_weight_grams = None
    product.save(using=database, update_fields=[
        'sale_unit', 'portion_weight_grams', 'stock_quantity',
    ])


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0031_alter_product_sale_unit'),
    ]

    operations = [
        migrations.RunPython(configure_smola_as_portions, restore_smola_to_pieces),
    ]
