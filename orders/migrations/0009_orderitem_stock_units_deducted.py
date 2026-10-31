from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0008_orderitem_trial_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='stock_units_deducted',
            field=models.PositiveIntegerField(default=0, verbose_name='Списано пакетиков'),
        ),
    ]
