from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_profile_default_address_profile_default_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(
                blank=True,
                upload_to='avatars/',
                verbose_name='Фото профиля',
            ),
        ),
    ]
