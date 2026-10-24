from django.db import migrations


def complete_sample_puer(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    ProductImage = apps.get_model('main', 'ProductImage')

    product = Product.objects.filter(slug='puer').first()
    if not product:
        return

    product.name = 'Пуэр прессованный'
    product.description = (
        'Прессованный китайский пуэр в компактном формате 50 г — вариант для знакомства '
        'с этой категорией чая или небольшого запаса дома. Отламывайте порцию непосредственно '
        'перед завариванием и регулируйте крепость количеством листа и временем настаивания.\n\n'
        'Заваривайте водой температурой 90–100 °C. Для гайвани начните с 5–7 г и коротких '
        'проливов; для кружки используйте меньше чая и подберите время по вкусу.'
    )
    product.attr_type = 'Пуэр'
    product.attr_origin = 'Китай, Юньнань'
    product.attr_temperature = '90–100°C'
    product.attr_time = '1–3 минуты'
    product.save(update_fields=[
        'name', 'description', 'attr_type', 'attr_origin',
        'attr_temperature', 'attr_time',
    ])

    image, _ = ProductImage.objects.get_or_create(
        product=product,
        image=product.image.name,
        defaults={'order': 0},
    )
    if image.order != 0:
        image.order = 0
        image.save(update_fields=['order'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_seed_puer_products'),
    ]

    operations = [
        migrations.RunPython(complete_sample_puer, migrations.RunPython.noop),
    ]
