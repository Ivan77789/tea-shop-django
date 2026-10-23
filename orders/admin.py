from django.contrib import admin
from .models import Order, OrderItem


# Позволяет добавлять/редактировать товары прямо внутри страницы заказа
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # Удобный поиск товара по ID, если их много
    extra = 0                   # Не показывать пустые строки


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Какие колонки показывать в общем списке заказов
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'phone', 'city', 'created']
    
    # Фильтры справа
    list_filter = ['created']
    
    # Поиск по этим полям
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'id']
    
    # Встраиваем таблицу с товарами внутрь заказа
    inlines = [OrderItemInline]
    
    # Группировка полей на странице редактирования заказа
    fieldsets = (
        ('Клиент', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Доставка', {
            'fields': ('city', 'address', 'comment')
        }),
        ('Статус', {
            'fields': ('created',),
        }),
    )
    
    # Поля, которые нельзя редактировать (только читать)
    readonly_fields = ['created']