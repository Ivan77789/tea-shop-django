from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0009_orderitem_stock_units_deducted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='unit',
            field=models.CharField(
                choices=[
                    ('piece', 'шт.'),
                    ('gram', 'г'),
                    ('cake', 'целый блин'),
                    ('trial', 'пробник'),
                    ('box', 'коробка'),
                ],
                default='piece',
                max_length=10,
            ),
        ),
    ]
