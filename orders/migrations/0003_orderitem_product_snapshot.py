from django.db import migrations, models
import django.db.models.deletion


def copy_product_names(apps, schema_editor):
    OrderItem = apps.get_model('orders', 'OrderItem')
    for item in OrderItem.objects.select_related('product').iterator():
        if item.product_id and item.product:
            item.product_name = item.product.name
            item.save(update_fields=['product_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_favorite'),
        ('orders', '0002_order_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='product_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Название товара на момент заказа'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.product'),
        ),
        migrations.RunPython(copy_product_names, migrations.RunPython.noop),
    ]
