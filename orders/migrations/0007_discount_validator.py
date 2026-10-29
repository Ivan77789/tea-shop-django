import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_orderitem_discount_percent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='discount_percent',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Скидка, %'),
        ),
    ]
