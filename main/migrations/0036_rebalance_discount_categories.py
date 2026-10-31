from django.db import migrations


def rebalance_discounts(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    Product.objects.using(database).filter(slug='shu-puer-menghai-drevnie-derevya-2017').update(
        discount_8g_percent=0,
        discount_25g_percent=0,
        discount_50g_percent=0,
        discount_100g_percent=0,
        whole_cake_discount_percent=0,
    )
    Product.objects.using(database).filter(slug='zhou-gui-niu-lan-keng').update(
        discount_8g_percent=3,
        discount_25g_percent=6,
        discount_50g_percent=10,
        discount_100g_percent=15,
        whole_cake_discount_percent=21,
    )


def restore_previous_discounts(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    Product.objects.using(database).filter(slug='shu-puer-menghai-drevnie-derevya-2017').update(
        discount_8g_percent=3,
        discount_25g_percent=6,
        discount_50g_percent=10,
        discount_100g_percent=15,
        whole_cake_discount_percent=21,
    )
    Product.objects.using(database).filter(slug='zhou-gui-niu-lan-keng').update(
        discount_8g_percent=0,
        discount_25g_percent=0,
        discount_50g_percent=0,
        discount_100g_percent=0,
        whole_cake_discount_percent=0,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0035_limit_catalog_discounts'),
    ]

    operations = [
        migrations.RunPython(rebalance_discounts, restore_previous_discounts),
    ]
