from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        verbose_name='Фото профиля',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    subscribe_news = models.BooleanField(default=False, verbose_name='Подписка на новости')

    # Адрес, который подставляется по умолчанию в оформлении заказа.
    default_city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    default_address = models.CharField(max_length=250, blank=True, verbose_name='Адрес')

    def __str__(self):
        return f'Профиль {self.user.username}'

# Этот код автоматически создает профиль, когда регистрируется новый пользователь
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
