from django.db import migrations


NEW_ARRIVAL_SLUGS = (
    'wuyi-rou-gui',
    'menku-shentaj-shen-z-ekosadiv-menku-2010',
)


def mark_new_arrivals(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    Product.objects.using(schema_editor.connection.alias).filter(
        slug__in=NEW_ARRIVAL_SLUGS,
    ).update(is_new=True)


def unmark_new_arrivals(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    Product.objects.using(schema_editor.connection.alias).filter(
        slug__in=NEW_ARRIVAL_SLUGS,
    ).update(is_new=False)


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0033_product_discount_percent_product_is_new'),
    ]

    operations = [
        migrations.RunPython(mark_new_arrivals, unmark_new_arrivals),
    ]
