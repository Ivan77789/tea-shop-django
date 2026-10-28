from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_profile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pending_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Неподтверждённый email'),
        ),
        migrations.AddField(
            model_name='profile',
            name='email_verification_sent_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время отправки письма подтверждения'),
        ),
    ]
