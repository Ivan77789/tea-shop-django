from django.db import migrations

from main.catalog_primary_images import PRIMARY_IMAGE_FILES


def set_metadata_primary_images(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    for slug, filename in PRIMARY_IMAGE_FILES.items():
        product = Product.objects.filter(slug=slug).select_related('category').first()
        if product is None:
            continue
        product.image = f'products/{product.category.slug}/{slug}/{filename}'
        product.save(update_fields=['image'])


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0023_connect_catalog_images'),
    ]

    operations = [
        migrations.RunPython(set_metadata_primary_images, migrations.RunPython.noop),
    ]
