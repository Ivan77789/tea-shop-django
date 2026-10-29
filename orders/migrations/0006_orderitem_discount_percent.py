from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_orderitem_cake_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Скидка, %'),
        ),
    ]
