from django.contrib import admin

from .models import Category, ContactMessage, ExtraAttribute, NewsletterSubscription, Product, ProductImage, SiteVisit


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


# Inline — картинки внутри товара
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ExtraAttributeInline(admin.TabularInline):
    model = ExtraAttribute
    extra = 1
    fields = ['order', 'name', 'value']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # В список выводим цену, цену пробника, остатки и артикул
    list_display = ['name', 'sku', 'price', 'discount_percent', 'is_new', 'trial_price', 'box_pack_count', 'sale_unit', 'available_gram_stock', 'box_count_in_stock', 'loose_pack_stock', 'available']
    list_filter = ['available', 'sale_unit', 'category']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ExtraAttributeInline]
    readonly_fields = ['available_gram_stock']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.sale_unit == Product.SALE_UNIT_GRAM:
            form.base_fields['stock_quantity'].label = 'Остаток открытого чая (г)'
            form.base_fields['price'].label = 'Цена за 50 г (грн)'
        elif obj and obj.sale_unit == Product.SALE_UNIT_PORTION:
            form.base_fields['stock_quantity'].label = 'Общий остаток чая (г)'
            form.base_fields['price'].label = 'Цена за одну порцию (грн)'
        elif obj:
            form.base_fields['stock_quantity'].label = 'Количество нераспечатанных коробок (шт.)'
            form.base_fields['price'].label = 'Цена за упаковку/коробку (грн)'
        else:
            form.base_fields['stock_quantity'].label = 'Остаток коробок или чая (г)'
            form.base_fields['price'].label = 'Цена в соответствии с выбранным типом продажи'
        form.base_fields['loose_pack_stock'].label = 'Количество отдельных пакетиков из вскрытых коробок (шт.)'
        return form

    @admin.display(description='Нераспечатанных коробок')
    def unopened_box_count(self, obj):
        if obj.sale_unit != Product.SALE_UNIT_PIECE:
            return '—'
        if obj.stock_quantity is None:
            return '∞'
        return obj.stock_quantity

    @admin.display(description='Пакетиков во вскрытой коробке')
    def loose_pack_remainder(self, obj):
        if obj.sale_unit != Product.SALE_UNIT_PIECE:
            return '—'
        return obj.loose_pack_stock

    @admin.display(description='Коробок в наличии')
    def box_count_in_stock(self, obj):
        return self.unopened_box_count(obj)

    @admin.display(description='Всего доступно (г)')
    def available_gram_stock(self, obj):
        if obj.sale_unit != Product.SALE_UNIT_GRAM:
            return '—'
        if obj.available_grams is None:
            return 'Без ограничения'
        return obj.available_grams

    # Группируем поля в админке для удобства
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'slug', 'sku', 'description', 'image', 'available', 'is_new', 'sale_unit'),
            'description': 'Для чая в коробках выберите тип продажи «Поштучно».'
        }),
        ('Цена и остатки', {
            'fields': ('price', 'discount_percent', 'weight', 'portion_weight_grams', 'box_pack_count', 'stock_quantity', 'available_gram_stock', 'loose_pack_stock', 'trial_price'),
            'description': 'Для развесного чая укажите цену за 50 г и остаток открытого чая. Общий доступный вес равен открытому чаю плюс вес блина, умноженный на число целых блинов. При продаже на развес сайт откроет нужное количество блинов и перенесёт остаток в открытый чай. Для порционного чая укажите общий остаток в граммах. Для коробочного чая укажите число нераспечатанных коробок и пакетиков из вскрытых коробок.',
        }),
        ('Развесной чай (скидки)', {
            'fields': ('discount_8g_percent', 'discount_25g_percent', 'discount_50g_percent', 'discount_100g_percent'),
            'description': 'Скидки на разные фасовки. Устанавливайте их только для товаров, которые участвуют в акции. Для поштучных товаров игнорируются.',
            'classes': ('collapse',), # Блок можно свернуть, чтобы не мешал
        }),
        ('Целый чайный блин', {
            'fields': ('whole_cake_weight_grams', 'whole_cake_stock', 'whole_cake_discount_percent'),
            'description': 'Заполните, если товар можно купить целым блином. Скидку указывайте только для товаров, участвующих в акции.',
            'classes': ('collapse',), # Блок можно свернуть
        }),
        ('Характеристики', {
            'fields': ('attr_type', 'attr_origin', 'attr_temperature', 'attr_time'),
            'description': 'Заполните характеристики для карточки товара'
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created', 'is_processed']


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'promo_sent_at', 'promo_used_at']
    search_fields = ['email']
    readonly_fields = ['email', 'subscribed_at', 'promo_sent_at', 'promo_used_at']
    ordering = ['-subscribed_at']


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ['visited_at', 'visitor_name', 'ip_address', 'path', 'device', 'status_code']
    list_filter = ['visited_at', 'status_code', 'method']
    search_fields = ['user__username', 'ip_address', 'path', 'user_agent']
    readonly_fields = [
        'user', 'ip_address', 'user_agent', 'path', 'method', 'status_code', 'visited_at'
    ]
    ordering = ['-visited_at']

    @admin.display(description='Пользователь')
    def visitor_name(self, obj):
        return obj.user.username if obj.user_id else 'Аноним'

    @admin.display(description='Устройство / браузер')
    def device(self, obj):
        return obj.user_agent[:80]

    def has_add_permission(self, request):
        return False
