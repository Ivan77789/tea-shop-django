from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_whole_cake_inventory'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='discount_8g_percent',
            field=models.PositiveSmallIntegerField(default=3, verbose_name='Скидка на порцию 8 г, %'),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_25g_percent',
            field=models.PositiveSmallIntegerField(default=6, verbose_name='Скидка на порцию 25 г, %'),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_50g_percent',
            field=models.PositiveSmallIntegerField(default=10, verbose_name='Скидка на порцию 50 г, %'),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_100g_percent',
            field=models.PositiveSmallIntegerField(default=15, verbose_name='Скидка на порцию 100 г, %'),
        ),
    ]
