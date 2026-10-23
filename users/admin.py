from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


# Встраиваем поля Профиля (телефон, подписка) прямо в страницу Пользователя
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Дополнительная информация (Телефон, Подписка)'


# Расширяем стандартную админку Пользователя
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    
    # Добавляем колонку "Телефон" в общий список пользователей
    list_display = ('username', 'email', 'first_name', 'get_phone', 'is_staff')
    
    def get_phone(self, obj):
        # Безопасно достаем телефон (если профиля вдруг нет, вернет прочерк)
        return obj.profile.phone if hasattr(obj, 'profile') else '-'
    get_phone.short_description = 'Телефон'


# Перерегистрируем Пользователя с нашими настройками
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)