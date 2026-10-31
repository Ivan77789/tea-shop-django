from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0037_newslettersubscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='newslettersubscription',
            name='promo_sent_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата отправки промокода'),
        ),
    ]
