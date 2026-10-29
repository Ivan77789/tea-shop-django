from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.db import models

from .constants import ORIGIN_CHOICES, TEMP_CHOICES, TIME_CHOICES, TYPE_CHOICES


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')

    def __str__(self):
        return self.name


class Product(models.Model):
    SALE_UNIT_PIECE = 'piece'
    SALE_UNIT_GRAM = 'gram'
    SALE_UNIT_CHOICES = [
        (SALE_UNIT_PIECE, 'Поштучно'),
        (SALE_UNIT_GRAM, 'На развес, граммы'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    weight = models.CharField(max_length=50, blank=True)
    sale_unit = models.CharField(
        max_length=10,
        choices=SALE_UNIT_CHOICES,
        default=SALE_UNIT_GRAM,
        verbose_name='Единица продажи',
    )
    stock_quantity = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name='Остаток на складе',
        help_text='Штуки для поштучных товаров, граммы для развесного чая. Пусто — складской учёт не задан.',
    )
    whole_cake_weight_grams = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Вес целого блина, г',
        help_text='Если товар можно купить целым блином, укажи его вес в граммах.',
    )
    whole_cake_stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Целых блинов на складе',
    )
    whole_cake_discount_percent = models.PositiveSmallIntegerField(
        default=21,
        validators=[MaxValueValidator(100)],
        verbose_name='Скидка на целый блин, %',
        help_text='Применяется к цене целого блина, рассчитанной из цены за 50 г.',
    )
    discount_8g_percent = models.PositiveSmallIntegerField(
        default=3, validators=[MaxValueValidator(100)], verbose_name='Скидка на порцию 8 г, %',
    )
    discount_25g_percent = models.PositiveSmallIntegerField(
        default=6, validators=[MaxValueValidator(100)], verbose_name='Скидка на порцию 25 г, %',
    )
    discount_50g_percent = models.PositiveSmallIntegerField(
        default=10, validators=[MaxValueValidator(100)], verbose_name='Скидка на порцию 50 г, %',
    )
    discount_100g_percent = models.PositiveSmallIntegerField(
        default=15, validators=[MaxValueValidator(100)], verbose_name='Скидка на порцию 100 г, %',
    )
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

    @property
    def order_step(self):
        return 50 if self.sale_unit == self.SALE_UNIT_GRAM else 1

    @property
    def order_unit_label(self):
        return 'г' if self.sale_unit == self.SALE_UNIT_GRAM else 'шт.'

    @property
    def price_unit_label(self):
        return 'за 50 г' if self.sale_unit == self.SALE_UNIT_GRAM else 'за шт.'

    @property
    def can_order(self):
        loose_stock_available = self.loose_can_order
        return loose_stock_available or self.whole_cake_available

    @property
    def loose_can_order(self):
        minimum_weight = 8 if self.sale_unit == self.SALE_UNIT_GRAM else 1
        return self.stock_quantity is None or self.stock_quantity >= minimum_weight

    @property
    def default_order_weight(self):
        if self.sale_unit != self.SALE_UNIT_GRAM or self.stock_quantity is None:
            return self.order_step
        for grams in (50, 25, 8):
            if self.stock_quantity >= grams:
                return grams
        return self.order_step

    @property
    def default_sale_mode(self):
        if self.sale_unit == self.SALE_UNIT_GRAM:
            return f'gram-{self.default_order_weight}'
        return self.sale_unit

    @property
    def whole_cake_available(self):
        return bool(self.whole_cake_weight_grams and self.whole_cake_stock > 0)

    @property
    def default_order_price(self):
        if self.sale_unit == self.SALE_UNIT_GRAM:
            grams = self.default_order_weight
            return self.discounted_line_total(grams, self.discount_for_weight(grams))
        return self.price

    @property
    def default_order_regular_price(self):
        if self.sale_unit == self.SALE_UNIT_GRAM:
            return self.line_total(self.default_order_weight)
        return self.price

    @property
    def default_discount_percent(self):
        if self.sale_unit == self.SALE_UNIT_GRAM:
            return self.discount_for_weight(self.default_order_weight)
        return 0

    @property
    def whole_cake_regular_price(self):
        if not self.whole_cake_weight_grams:
            return Decimal('0.00')
        return self.line_total(self.whole_cake_weight_grams)

    @property
    def whole_cake_price(self):
        discount = Decimal(100 - min(self.whole_cake_discount_percent, 100)) / Decimal('100')
        return (self.whole_cake_regular_price * discount).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    def discount_for_weight(self, grams):
        discount_fields = {
            8: self.discount_8g_percent,
            25: self.discount_25g_percent,
            50: self.discount_50g_percent,
            100: self.discount_100g_percent,
        }
        return min(discount_fields.get(int(grams), 0), 100)

    def discounted_line_total(self, grams, discount_percent):
        discount = Decimal(100 - min(max(int(discount_percent), 0), 100)) / Decimal('100')
        amount = self.price * Decimal(grams) / Decimal('50') * discount
        return amount.quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

    def line_total(self, quantity):
        multiplier = Decimal(quantity)
        if self.sale_unit == self.SALE_UNIT_GRAM:
            multiplier /= Decimal('50')
        return (self.price * multiplier).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


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


class SiteVisit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='site_visits',
        verbose_name='Пользователь',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP-адрес')
    user_agent = models.TextField(blank=True, verbose_name='Браузер и устройство')
    path = models.CharField(max_length=500, verbose_name='Страница')
    method = models.CharField(max_length=10, verbose_name='Метод запроса')
    status_code = models.PositiveSmallIntegerField(verbose_name='Код ответа')
    visited_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время посещения')

    class Meta:
        ordering = ['-visited_at']
        verbose_name = 'Посещение сайта'
        verbose_name_plural = 'Посещения сайта'

    def __str__(self):
        visitor = self.user.username if self.user_id else 'Аноним'
        return f'{visitor}: {self.path} ({self.visited_at:%Y-%m-%d %H:%M})'
