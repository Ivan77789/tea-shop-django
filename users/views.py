from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from main.models import Favorite
from orders.models import Order  # Проверь, что импортировано

from .forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
    ProfileUpdateForm,
    UserUpdateForm,
)
from .models import Profile


# Вход
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True # Если уже вошел - на главную

# Регистрация
def register(request):
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Автоматически входим после регистрации
            return redirect('main:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})

# Выход
def logout_view(request):
    logout(request)
    return redirect('main:index')



@login_required
def account(request):
    return render(request, 'users/account.html', {'user': request.user})

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    # Получаем сами товары из избранного
    products = [fav.product for fav in favorites]
    return render(request, 'main/favorites.html', {'products': products})



@login_required
def orders_list(request):
    # Берем заказы только этого пользователя, сначала новые
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'users/orders_list.html', {'orders': orders})





@login_required
def profile_edit(request):
    # Проверяем, есть ли профиль, если нет - создаем
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        # Привязываем данные из POST-запроса к формам
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        # Если обе формы заполнены корректно
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()  # Сохраняем имя и email
            p_form.save()  # Сохраняем телефон и подписку
            messages.success(request, 'Ваши данные успешно обновлены!')
            return redirect('users:profile_edit')
    else:
        # Если это просто загрузка страницы, показываем текущие данные
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile_edit.html', context)




@login_required
def address_list(request):
    # Пока просто отдаем шаблон-заглушку
    return render(request, 'users/address_list.html')