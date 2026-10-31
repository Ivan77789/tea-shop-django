from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0036_rebalance_discount_categories'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('subscribed_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')),
                ('promo_used_at', models.DateTimeField(blank=True, null=True, verbose_name='Дата использования промокода')),
            ],
            options={
                'verbose_name': 'Подписка на новости',
                'verbose_name_plural': 'Подписки на новости',
                'ordering': ['-subscribed_at'],
            },
        ),
    ]
