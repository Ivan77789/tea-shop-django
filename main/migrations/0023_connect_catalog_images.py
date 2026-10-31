from django.db import migrations

from main.catalog_primary_images import PRIMARY_IMAGE_FILES, PRODUCT_IMAGE_COUNTS


def connect_images(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    ProductImage = apps.get_model('main', 'ProductImage')

    for slug, primary_filename in PRIMARY_IMAGE_FILES.items():
        product = Product.objects.filter(slug=slug).select_related('category').first()
        if product is None:
            continue

        directory = f'products/{product.category.slug}/{slug}'
        product.image = f'{directory}/{primary_filename}'
        product.save(update_fields=['image'])

        ProductImage.objects.filter(product=product).delete()
        ProductImage.objects.bulk_create([
            ProductImage(
                product=product,
                image=f'{directory}/{index:02d}.png',
                order=index - 1,
            )
            for index in range(1, PRODUCT_IMAGE_COUNTS[slug] + 1)
        ])


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0022_product_sku_product_trial_stock_and_more'),
    ]

    operations = [
        migrations.RunPython(connect_images, migrations.RunPython.noop),
    ]
