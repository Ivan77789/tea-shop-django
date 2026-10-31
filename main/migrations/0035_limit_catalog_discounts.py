from django.db import migrations, models
import django.core.validators


# 10 из 32 товаров (около 31%), равномерно по четырём категориям.
PROMOTION_SLUGS = (
    'menku-shentaj-shen-z-ekosadiv-menku-2010',
    'shu-puer-vpechatlenie-yiwu',
    'shu-puer-menghai-drevnie-derevya-2017',
    'zhasminovyy-glaz-feniksa',
    'meijiawu-longjing',
    'taiping-hou-kui',
    'gaba-yunnan-bai-cha',
    'wuyi-rou-gui',
    'zolotye-tsvety',
    'fuzhunshan-anhua-heicha-2017',
)


def keep_discounts_on_selected_products(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    Product.objects.using(database).all().update(
        discount_8g_percent=0,
        discount_25g_percent=0,
        discount_50g_percent=0,
        discount_100g_percent=0,
        whole_cake_discount_percent=0,
    )
    Product.objects.using(database).filter(slug__in=PROMOTION_SLUGS).update(
        discount_8g_percent=3,
        discount_25g_percent=6,
        discount_50g_percent=10,
        discount_100g_percent=15,
        whole_cake_discount_percent=21,
    )


def restore_previous_default_discounts(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    database = schema_editor.connection.alias
    Product.objects.using(database).all().update(
        discount_8g_percent=3,
        discount_25g_percent=6,
        discount_50g_percent=10,
        discount_100g_percent=15,
        whole_cake_discount_percent=21,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0034_mark_catalog_new_arrivals'),
    ]

    operations = [
        migrations.RunPython(keep_discounts_on_selected_products, restore_previous_default_discounts),
        migrations.AlterField(
            model_name='product',
            name='discount_8g_percent',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на 8 г, %'),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount_25g_percent',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на 25 г, %'),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount_50g_percent',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на 50 г, %'),
        ),
        migrations.AlterField(
            model_name='product',
            name='discount_100g_percent',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на 100 г, %'),
        ),
        migrations.AlterField(
            model_name='product',
            name='whole_cake_discount_percent',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на целый блин, %'),
        ),
    ]
