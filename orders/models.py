from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models
from main.models import Product


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Новый'),
        (STATUS_CONFIRMED, 'Подтверждён'),
        (STATUS_CANCELLED, 'Отменён'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь') # ← НОВОЕ ПОЛЕ


    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=250, verbose_name='Адрес')
    city = models.CharField(max_length=100, verbose_name='Город')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус',
    )
    promo_code = models.CharField(max_length=30, blank=True, default='', verbose_name='Промокод')
    promo_discount_amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        default=0,
        verbose_name='Скидка по промокоду (грн)',
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.id}'

    def get_total_cost(self):
        return max(self.get_items_subtotal() - self.promo_discount_amount, Decimal('0.00'))

    def get_items_subtotal(self):
        return sum((item.get_cost() for item in self.items.all()), Decimal('0.00'))


class OrderItem(models.Model):
    UNIT_PIECE = 'piece'
    UNIT_GRAM = 'gram'
    UNIT_CAKE = 'cake'
    UNIT_TRIAL = 'trial'
    UNIT_BOX = 'box'
    UNIT_PORTION = 'portion'
    UNIT_CHOICES = [
        (UNIT_PIECE, 'шт.'),
        (UNIT_GRAM, 'г'),
        (UNIT_CAKE, 'целый блин'),
        (UNIT_TRIAL, 'пробник'),
        (UNIT_BOX, 'коробка'),
        (UNIT_PORTION, 'порция'),
    ]

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200, blank=True, verbose_name='Название товара на момент заказа')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=UNIT_PIECE)
    discount_percent = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(100)], verbose_name='Скидка, %'
    )
    stock_deducted = models.BooleanField(default=False, verbose_name='Списан со склада')
    stock_units_deducted = models.PositiveIntegerField(default=0, verbose_name='Списано пакетиков')

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        quantity = Decimal(self.quantity)
        if self.unit == self.UNIT_GRAM:
            quantity /= Decimal('50')
        discount = Decimal(100 - min(self.discount_percent, 100)) / Decimal('100')
        return (self.price * quantity * discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
