from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import Adjust, ResizeToFill

from .catalog_primary_images import PRIMARY_IMAGE_FILES
from .constants import ORIGIN_CHOICES, TEMP_CHOICES, TIME_CHOICES, TYPE_CHOICES


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')

    def __str__(self):
        return self.name


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата подписки')
    promo_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки промокода')
    promo_used_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата использования промокода')

    class Meta:
        verbose_name = 'Подписка на новости'
        verbose_name_plural = 'Подписки на новости'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

class Product(models.Model):
    SALE_UNIT_PIECE = 'piece'
    SALE_UNIT_GRAM = 'gram'
    SALE_UNIT_PORTION = 'portion'
    SALE_UNIT_CHOICES = [
        (SALE_UNIT_PIECE, 'Поштучно (Коробки, упаковки)'),
        (SALE_UNIT_GRAM, 'На развес (Граммы)'),
        (SALE_UNIT_PORTION, 'Порционно (обёрнутые кусочки)'),
    ]

    # === ОСНОВНАЯ ИНФОРМАЦИЯ ===
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL (слаг)')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='products/', verbose_name='Главное изображение')
    available = models.BooleanField(default=True, verbose_name='Доступен для заказа')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    sku = models.CharField(max_length=50, blank=True, verbose_name='Артикул (SKU)')

    sale_unit = models.CharField(
        max_length=10,
        choices=SALE_UNIT_CHOICES,
        default=SALE_UNIT_GRAM,
        verbose_name='Тип продажи',
        help_text='Выберите формат: развесной чай, коробки/упаковки или отдельные обёрнутые порции.'
    )

    # === БЛОК 1: ДЛЯ ПОШТУЧНЫХ ТОВАРОВ (КОРОБКИ) ===
    price = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='Цена за упаковку/коробку (грн)', default=0)
    discount_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name='Скидка на товар, %',
        help_text='Общая скидка на коробку или порцию. Для развесного чая применяется, если она выше скидки выбранного веса.',
    )
    is_new = models.BooleanField(default=False, verbose_name='Показывать отметку «Новинка»')
    stock_quantity = models.PositiveIntegerField(
        null=True, blank=True, default=0,
        verbose_name='Нераспечатанных коробок (шт.)',
        help_text='Для чая на развес — остаток открытого чая в граммах. Закрытые блины учитываются отдельно и входят в общий доступный вес.'
    )
    loose_pack_stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Пакетиков из вскрытых коробок (шт.)',
        help_text='Отдельные пакетики, оставшиеся после вскрытия коробок. Пробник расходует один пакетик.',
    )
    trial_price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        verbose_name='Цена за пробник (грн)',
        help_text='Оставьте пустым, если пробников нет.'
    )
    box_pack_count = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Пакетиков в коробке',
        help_text='Количество индивидуальных пакетиков в одной коробке/упаковке. Для обычных товаров оставьте 1.',
    )
    portion_weight_grams = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Вес одной порции (г)',
        help_text='Для чая в отдельных обёртках укажите вес одной порции: например 2, 3 или 5 г.',
    )

    # === БЛОК 2: ДЛЯ РАЗВЕСНОГО ЧАЯ (ГРАММЫ) ===
    # Цена за 50г берется из поля price выше
    discount_8g_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name='Скидка на 8 г, %')
    discount_25g_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name='Скидка на 25 г, %')
    discount_50g_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name='Скидка на 50 г, %')
    discount_100g_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name='Скидка на 100 г, %')

    # === БЛОК 3: ДЛЯ ЦЕЛЫХ БЛИНОВ (ПУЭРЫ) ===
    whole_cake_weight_grams = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name='Вес целого блина (г)',
        help_text='Если товар можно купить целым блином, укажите его вес в граммах.'
    )
    whole_cake_stock = models.PositiveIntegerField(default=0, verbose_name='Остаток целых блинов (шт.)')
    whole_cake_discount_percent = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)], verbose_name='Скидка на целый блин, %')
    
    # === ХАРАКТЕРИСТИКИ ===
    weight = models.CharField(max_length=50, blank=True, verbose_name='Вес упаковки (текст)', help_text='Например: 17 г, 100 г')
    attr_type = models.CharField(max_length=100, choices=TYPE_CHOICES, blank=True, verbose_name='Тип')
    attr_origin = models.CharField(max_length=100, choices=ORIGIN_CHOICES, blank=True, verbose_name='Место происхождения')
    attr_temperature = models.CharField(max_length=100, choices=TEMP_CHOICES, blank=True, verbose_name='Температура заваривания')
    attr_time = models.CharField(max_length=100, choices=TIME_CHOICES, blank=True, verbose_name='Время заваривания')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'                             

    def __str__(self):
        return self.name

    @property
    def display_image_url(self):
        """Prefer the first-downloaded image identified from source file metadata."""
        primary_filename = PRIMARY_IMAGE_FILES.get(self.slug)
        if primary_filename:
            primary_path = f'products/{self.category.slug}/{self.slug}/{primary_filename}'
            if default_storage.exists(primary_path):
                return default_storage.url(primary_path)

        candidate_dirs = (
            f'products/{self.category.slug}/{self.slug}',
            f'products/{self.slug}',
        )
        for directory in candidate_dirs:
            try:
                _, filenames = default_storage.listdir(directory)
            except (FileNotFoundError, NotImplementedError):
                continue
            images = [
                name for name in filenames
                if name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))
            ]
            images.sort(key=lambda name: (name.lower().startswith('image_'), name.lower()))
            if images:
                return default_storage.url(f'{directory}/{images[0]}')
        if self.image and default_storage.exists(self.image.name):
            return self.image.url
        return None

    @property
    def display_gallery_urls(self):
        """Return existing gallery files with the metadata-selected primary first."""
        urls = []
        primary_url = self.display_image_url
        if primary_url:
            urls.append(primary_url)
        for directory in (
            f'products/{self.category.slug}/{self.slug}',
            f'products/{self.slug}',
        ):
            try:
                _, filenames = default_storage.listdir(directory)
            except (FileNotFoundError, NotImplementedError):
                continue
            filenames = [
                name for name in filenames
                if name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))
            ]
            imported_sequence = [
                name for name in filenames
                if len(name) == 6 and name[:2].isdigit() and name.lower().endswith('.png')
            ]
            if imported_sequence:
                filenames = imported_sequence
            filenames.sort(key=lambda name: (name.lower().startswith('image_'), name.lower()))
            urls.extend(
                url for url in (default_storage.url(f'{directory}/{name}') for name in filenames)
                if url not in urls
            )
        for image in self.images.all():
            if image.image and default_storage.exists(image.image.name):
                if image.image.url not in urls:
                    urls.append(image.image.url)
        return urls

    # === СВОЙСТВА (ЛОГИКА) ===
    
    @property
    def can_order(self):
        if self.sale_unit == self.SALE_UNIT_PORTION:
            return self.portion_stock_available is None or self.portion_stock_available > 0
        if self.sale_unit == self.SALE_UNIT_PIECE:
            return self.box_stock_available > 0 or self.trial_can_order
        # Для развеса учитываем открытый остаток и вес нераспечатанных блинов.
        return self.can_supply_grams(8) or self.whole_cake_available

    @property
    def available_grams(self):
        """Sellable weight: loose tea plus all unopened whole cakes."""
        if self.stock_quantity is None:
            return None
        if self.sale_unit != self.SALE_UNIT_GRAM or not self.whole_cake_weight_grams:
            return self.stock_quantity
        return self.stock_quantity + self.whole_cake_stock * self.whole_cake_weight_grams

    def can_supply_grams(self, grams):
        available = self.available_grams
        return available is None or available >= grams

    def consume_gram_stock(self, grams):
        """Use opened tea first, opening the fewest cakes needed to fulfill a sale."""
        if self.stock_quantity is None:
            return
        available = self.available_grams
        if grams < 1 or grams > available:
            raise ValueError(f'В наличии только {available} г чая.')

        loose_grams = self.stock_quantity
        if loose_grams < grams:
            cake_weight = self.whole_cake_weight_grams or 0
            if not cake_weight:
                raise ValueError(f'В наличии только {loose_grams} г чая.')
            grams_to_open = grams - loose_grams
            cakes_to_open = (grams_to_open + cake_weight - 1) // cake_weight
            if cakes_to_open > self.whole_cake_stock:
                raise ValueError(f'В наличии только {available} г чая.')
            self.whole_cake_stock -= cakes_to_open
            loose_grams += cakes_to_open * cake_weight
        self.stock_quantity = loose_grams - grams

    @property
    def default_order_price(self):
        if self.sale_unit == self.SALE_UNIT_GRAM and not self.loose_can_order and self.whole_cake_available:
            return self.whole_cake_price
        if self.sale_unit == self.SALE_UNIT_PORTION:
            return self._price_after_discount(self.price, self.default_discount_percent)
        if self.sale_unit == self.SALE_UNIT_GRAM:
            grams = self.default_order_weight
            return self.discounted_line_total(grams, self.default_discount_percent)
        if self.default_sale_mode == 'piece-trial' and self.trial_price is not None:
            return self.trial_price
        return self._price_after_discount(self.price, self.default_discount_percent)

    @property
    def default_order_regular_price(self):
        if self.sale_unit == self.SALE_UNIT_GRAM and not self.loose_can_order and self.whole_cake_available:
            return self.whole_cake_regular_price
        if self.sale_unit == self.SALE_UNIT_GRAM:
            return self.line_total(self.default_order_weight)
        if self.default_sale_mode == 'piece-trial' and self.trial_price is not None:
            return self.trial_price
        return self.price

    @property
    def default_discount_percent(self):
        if self.sale_unit == self.SALE_UNIT_GRAM:
            if not self.loose_can_order and self.whole_cake_available:
                return min(self.whole_cake_discount_percent, 100)
            return max(self.discount_percent, self.discount_for_weight(self.default_order_weight))
        if self.sale_unit == self.SALE_UNIT_PIECE and self.default_sale_mode == 'piece-trial':
            return 0
        return min(self.discount_percent, 100)

    @staticmethod
    def _price_after_discount(price, discount_percent):
        discount = Decimal(100 - min(max(int(discount_percent), 0), 100)) / Decimal('100')
        return (price * discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def default_sale_mode(self):
        if self.sale_unit == self.SALE_UNIT_PORTION:
            return self.SALE_UNIT_PORTION
        if self.sale_unit == self.SALE_UNIT_GRAM:
            return f'gram-{self.default_order_weight}'
        if (
            self.sale_unit == self.SALE_UNIT_PIECE
            and self.stock_quantity is not None
            and self.box_stock_available < 1
            and self.trial_price is not None
            and self.trial_stock_available > 0
        ):
            return 'piece-trial'
        return 'piece-box'

    @property
    def box_stock_available(self):
        if self.stock_quantity is None:
            return 99
        return self.stock_quantity

    @property
    def trial_stock_available(self):
        if self.stock_quantity is None:
            return None
        return self.loose_pack_stock + self.stock_quantity * max(self.box_pack_count, 1)

    @property
    def portion_stock_available(self):
        if not self.portion_weight_grams:
            return 0
        if self.stock_quantity is None:
            return None
        return self.stock_quantity // self.portion_weight_grams

    @property
    def trial_can_order(self):
        return self.trial_price is not None and (
            self.trial_stock_available is None or self.trial_stock_available > 0
        )

    def consume_trial_packs(self, quantity):
        """Use loose sachets first, opening the fewest boxes needed for the remainder."""
        if self.stock_quantity is None:
            return
        packs_per_box = max(self.box_pack_count, 1)
        packs_after_loose = max(quantity - self.loose_pack_stock, 0)
        boxes_to_open = (packs_after_loose + packs_per_box - 1) // packs_per_box
        if boxes_to_open > self.stock_quantity:
            raise ValueError('Недостаточно пакетиков на складе.')
        self.stock_quantity -= boxes_to_open
        self.loose_pack_stock += boxes_to_open * packs_per_box - quantity

    @property
    def default_order_weight(self):
        if self.sale_unit != self.SALE_UNIT_GRAM or self.available_grams is None:
            return 50 # Для штучных не важно
        for grams in (50, 25, 8):
            if self.available_grams >= grams:
                return grams
        return 50

    @property
    def loose_can_order(self):
        if self.sale_unit == self.SALE_UNIT_PORTION:
            return self.portion_stock_available is None or self.portion_stock_available > 0
        if self.sale_unit == self.SALE_UNIT_PIECE:
            return self.stock_quantity is None or self.box_stock_available > 0
        return self.can_supply_grams(8)

    @property
    def can_sell_8g(self):
        return self.can_supply_grams(8)

    @property
    def can_sell_25g(self):
        return self.can_supply_grams(25)

    @property
    def can_sell_50g(self):
        return self.can_supply_grams(50)

    @property
    def can_sell_100g(self):
        return self.can_supply_grams(100)

    @property
    def whole_cake_available(self):
        return bool(self.whole_cake_weight_grams and self.whole_cake_stock > 0)

    @property
    def price_unit_label(self):
        if self.sale_unit == self.SALE_UNIT_PORTION:
            return 'за порцию'
        if self.sale_unit == self.SALE_UNIT_GRAM:
            return 'за 50 г'
        return 'за упаковку'

    @property
    def order_unit_label(self):
        return 'г' if self.sale_unit == self.SALE_UNIT_GRAM else 'шт.'

    @property
    def order_step(self):
        return 50 if self.sale_unit == self.SALE_UNIT_GRAM else 1

    @property
    def whole_cake_regular_price(self):
        if not self.whole_cake_weight_grams: return Decimal('0.00')
        return self.line_total(self.whole_cake_weight_grams)

    @property
    def whole_cake_price(self):
        discount = Decimal(100 - min(self.whole_cake_discount_percent, 100)) / Decimal('100')
        return (self.whole_cake_regular_price * discount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def discount_for_weight(self, grams):
        discount_fields = {
            8: self.discount_8g_percent, 25: self.discount_25g_percent,
            50: self.discount_50g_percent, 100: self.discount_100g_percent,
        }
        return min(discount_fields.get(int(grams), 0), 100)

    def discounted_line_total(self, grams, discount_percent):
        discount = Decimal(100 - min(max(int(discount_percent), 0), 100)) / Decimal('100')
        amount = self.price * Decimal(grams) / Decimal('50') * discount
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

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
