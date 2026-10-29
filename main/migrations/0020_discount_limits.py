import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_product_gram_discounts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product', name='whole_cake_discount_percent',
            field=models.PositiveSmallIntegerField(default=21, help_text='Применяется к цене целого блина, рассчитанной из цены за 50 г.', validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на целый блин, %'),
        ),
        migrations.AlterField(
            model_name='product', name='discount_8g_percent',
            field=models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на порцию 8 г, %'),
        ),
        migrations.AlterField(
            model_name='product', name='discount_25g_percent',
            field=models.PositiveSmallIntegerField(default=6, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на порцию 25 г, %'),
        ),
        migrations.AlterField(
            model_name='product', name='discount_50g_percent',
            field=models.PositiveSmallIntegerField(default=10, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на порцию 50 г, %'),
        ),
        migrations.AlterField(
            model_name='product', name='discount_100g_percent',
            field=models.PositiveSmallIntegerField(default=15, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка на порцию 100 г, %'),
        ),
    ]
