from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_product_inventory'),
        ('orders', '0003_orderitem_product_snapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Новый'),
                    ('confirmed', 'Подтверждён'),
                    ('cancelled', 'Отменён'),
                ],
                default='pending',
                max_length=12,
                verbose_name='Статус',
            ),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='unit',
            field=models.CharField(
                choices=[('piece', 'шт.'), ('gram', 'г')],
                default='piece',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='stock_deducted',
            field=models.BooleanField(default=False, verbose_name='Списан со склада'),
        ),
    ]
