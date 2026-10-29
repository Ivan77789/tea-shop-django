from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_sitevisit'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sale_unit',
            field=models.CharField(
                choices=[('piece', 'Поштучно'), ('gram', 'На развес, граммы')],
                default='piece',
                max_length=10,
                verbose_name='Единица продажи',
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(
                blank=True,
                default=None,
                help_text='Штуки для поштучных товаров, граммы для развесного чая. Пусто — складской учёт не задан.',
                null=True,
                verbose_name='Остаток на складе',
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text='Штуки для поштучных товаров, граммы для развесного чая. Пусто — складской учёт не задан.',
                null=True,
                verbose_name='Остаток на складе',
            ),
        ),
    ]
