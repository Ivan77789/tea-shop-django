from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0011_alter_orderitem_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='promo_code',
            field=models.CharField(default='', max_length=30, blank=True, verbose_name='Промокод'),
        ),
        migrations.AddField(
            model_name='order',
            name='promo_discount_amount',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=9, verbose_name='Скидка по промокоду (грн)'),
        ),
    ]
