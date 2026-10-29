from django.contrib import admin

from .models import Category, ContactMessage, ExtraAttribute, Product, ProductImage, SiteVisit


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
    list_display = ['name', 'price', 'sale_unit', 'stock_quantity', 'whole_cake_stock', 'available', 'created']
    list_filter = ['available', 'category']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ExtraAttributeInline]

# Группируем поля в админке
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'slug', 'description', 'price', 'weight', 'sale_unit', 'stock_quantity', 'image', 'available'),
            'description': 'Для товара на развес цена задаётся за 50 г, остаток — в граммах. Для поштучного товара цена и остаток задаются за штуку. Пустой остаток отключает складской учёт; 0 означает, что товара нет в наличии.',
        }),
        ('Целый чайный блин', {
            'fields': ('whole_cake_weight_grams', 'whole_cake_stock', 'whole_cake_discount_percent'),
            'description': 'Заполните вес и количество целых блинов, чтобы показать покупателю покупку целого блина. Скидка применяется к цене за весь блин, рассчитанной из цены за 50 г.',
        }),
        ('Скидки на развес', {
            'fields': ('discount_8g_percent', 'discount_25g_percent', 'discount_50g_percent', 'discount_100g_percent'),
            'description': 'Скидка применяется к цене выбранной фасовки. У каждого размера свой процент.',
        }),
        ('Характеристики', {
            'fields': ('attr_type', 'attr_origin', 'attr_temperature', 'attr_time'),
            'description': 'Заполните характеристики для карточки товара'
        }),
    )    

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created', 'is_processed']


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
