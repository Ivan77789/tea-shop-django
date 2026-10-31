from django.db import migrations


PACKAGED_ROU_GUI_SLUGS = (
    'wuyi-rou-gui',
    'hu-xiao-yan-rou-gui',
    'yan-zhi-ke-rou-gui',
)


def configure_packaged_rou_gui(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    Product.objects.filter(slug__in=PACKAGED_ROU_GUI_SLUGS).update(sale_unit='piece')


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0025_product_box_pack_count'),
    ]

    operations = [
        migrations.RunPython(configure_packaged_rou_gui, migrations.RunPython.noop),
    ]
