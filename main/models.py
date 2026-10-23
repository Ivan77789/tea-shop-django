from django.contrib.auth.models import User
from django.db import models

from .constants import ORIGIN_CHOICES, TEMP_CHOICES, TIME_CHOICES, TYPE_CHOICES


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    weight = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='products/')
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)




    attr_type = models.CharField(max_length=100, choices=TYPE_CHOICES, blank=True, verbose_name='Тип')
    attr_origin = models.CharField(max_length=100, choices=ORIGIN_CHOICES, blank=True, verbose_name='Место происхождения')
    
    # Для температуры и времени используем choices
    attr_temperature = models.CharField(
        max_length=100, 
        choices=TEMP_CHOICES, 
        blank=True, 
        verbose_name='Температура заваривания'
    )
    attr_time = models.CharField(
        max_length=100, 
        choices=TIME_CHOICES, 
        blank=True, 
        verbose_name='Время заваривания'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'                             

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар'
    )
    image = models.ImageField(upload_to='products/', verbose_name='Картинка')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Картинка товара'
        verbose_name_plural = 'Картинки товаров'

    def __str__(self):
        return f'Картинка #{self.id} для {self.product.name}'    


class ExtraAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='extra_attributes',
        verbose_name='Товар'
    )
    name = models.CharField(max_length=100, verbose_name='Название')
    value = models.CharField(max_length=255, verbose_name='Значение')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        ordering = ['order']
        verbose_name = 'Дополнительную характеристику'
        verbose_name_plural = 'Дополнительные характеристики'

    def __str__(self):
        return f'{self.name}: {self.value}'


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    message = models.TextField(verbose_name='Сообщение')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    is_processed = models.BooleanField(default=False, verbose_name='Обработано')

    class Meta:
        ordering = ['-created']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.name} ({self.email})'





class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product') # Один товар нельзя добавить дважды
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'    