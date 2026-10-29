from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_inventory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='unit',
            field=models.CharField(
                choices=[('piece', 'шт.'), ('gram', 'г'), ('cake', 'целый блин')],
                default='piece',
                max_length=10,
            ),
        ),
    ]
