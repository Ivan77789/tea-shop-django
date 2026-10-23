from django.contrib import admin

from .models import Category, ContactMessage, ExtraAttribute, Product, ProductImage


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
    list_display = ['name', 'price', 'available', 'created']
    list_filter = ['available', 'category']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ExtraAttributeInline]

# Группируем поля в админке
    fieldsets = (
        ('Основная информация', {
            'fields': ('category', 'name', 'slug', 'description', 'price', 'weight', 'image', 'available')
        }),
        ('Характеристики', {
            'fields': ('attr_type', 'attr_origin', 'attr_temperature', 'attr_time'),
            'description': 'Заполните характеристики для карточки товара'
        }),
    )    

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created', 'is_processed']    