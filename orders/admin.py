from django.contrib import admin
from django.contrib import messages
from django.db import transaction

from main.models import Product
from .models import Order, OrderItem


# Позволяет добавлять/редактировать товары прямо внутри страницы заказа
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product'] # Удобный поиск товара по ID, если их много
    extra = 0                   # Не показывать пустые строки
    readonly_fields = ['product', 'product_name', 'price', 'quantity', 'unit', 'discount_percent', 'stock_deducted']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Какие колонки показывать в общем списке заказов
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'promo_code', 'status', 'created']
    
    # Фильтры справа
    list_filter = ['status', 'created']
    
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
            'fields': ('status', 'created'),
        }),
        ('Скидка на первый заказ', {
            'fields': ('promo_code', 'promo_discount_amount'),
        }),
    )
    
    # Поля, которые нельзя редактировать (только читать)
    readonly_fields = ['created', 'promo_code', 'promo_discount_amount']

    def _restore_stock(self, order):
        for item in order.items.filter(stock_deducted=True):
            if item.product_id:
                product = Product.objects.select_for_update().filter(pk=item.product_id).first()
                if product is not None:
                    if item.unit == OrderItem.UNIT_CAKE:
                        product.whole_cake_stock += item.quantity
                        product.save(update_fields=['whole_cake_stock'])
                    elif item.unit == OrderItem.UNIT_TRIAL:
                        product.loose_pack_stock += item.stock_units_deducted or item.quantity
                        product.save(update_fields=['loose_pack_stock'])
                    elif item.unit == OrderItem.UNIT_BOX:
                        deducted = item.stock_units_deducted
                        packs_per_box = max(product.box_pack_count, 1)
                        # Older orders stored sachets deducted; newer ones store boxes.
                        if not deducted:
                            deducted = item.quantity * packs_per_box
                        if packs_per_box > 1 and deducted == item.quantity * packs_per_box:
                            boxes, loose_packs = divmod(deducted, packs_per_box)
                            product.stock_quantity = (product.stock_quantity or 0) + boxes
                            product.loose_pack_stock += loose_packs
                            product.save(update_fields=['stock_quantity', 'loose_pack_stock'])
                        else:
                            product.stock_quantity = (product.stock_quantity or 0) + item.quantity
                            product.save(update_fields=['stock_quantity'])
                    else:
                        units_to_restore = item.stock_units_deducted
                        if not units_to_restore:
                            units_to_restore = item.quantity * product.box_pack_count if item.unit in (
                                OrderItem.UNIT_BOX, OrderItem.UNIT_PIECE
                            ) else item.quantity
                        product.stock_quantity = (product.stock_quantity or 0) + units_to_restore
                        product.save(update_fields=['stock_quantity'])
            item.stock_deducted = False
            item.save(update_fields=['stock_deducted'])

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = Order.objects.get(pk=obj.pk).status
            if previous_status == Order.STATUS_CANCELLED and obj.status != Order.STATUS_CANCELLED:
                self.message_user(
                    request,
                    'Отменённый заказ нельзя повторно открыть: остатки уже возвращены на склад.',
                    level=messages.ERROR,
                )
                obj.status = Order.STATUS_CANCELLED

        with transaction.atomic():
            if change and obj.status == Order.STATUS_CANCELLED and previous_status != Order.STATUS_CANCELLED:
                self._restore_stock(obj)
            super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        with transaction.atomic():
            self._restore_stock(obj)
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        with transaction.atomic():
            for order in queryset.select_for_update():
                self._restore_stock(order)
            super().delete_queryset(request, queryset)
