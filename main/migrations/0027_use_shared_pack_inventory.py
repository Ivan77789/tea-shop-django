from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0026_configure_packaged_rou_gui'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='trial_stock',
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text='Общий остаток индивидуальных пакетиков. Для коробок укажите: количество коробок × пакетиков в коробке.',
                null=True,
                verbose_name='Остаток пакетиков (шт.)',
            ),
        ),
    ]
