import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0024_metadata_primary_product_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='box_pack_count',
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text='Количество индивидуальных пакетиков в одной коробке/упаковке. Для обычных товаров оставьте 1.',
                validators=[django.core.validators.MinValueValidator(1)],
                verbose_name='Пакетиков в коробке',
            ),
        ),
    ]
