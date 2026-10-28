import re
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from users.forms import ProfileUpdateForm, UserUpdateForm
from users.models import Profile

from .forms import ContactForm
from .models import Category, Favorite, Product


def index(request):
    products = Product.objects.filter(available=True)[:4]   # первые 4 товара
    return render(request, 'main/index.html', {'products': products})




def get_filtered_products(request):
    """Общая логика фильтрации — для обоих вьюх."""
    products = Product.objects.filter(available=True)

    search_query = request.GET.get('q', '').strip()[:100]
    for word in search_query.split():
        search_pattern = re.escape(word)
        products = products.filter(
            Q(name__iregex=search_pattern)
            | Q(description__iregex=search_pattern)
            | Q(category__name__iregex=search_pattern)
            | Q(weight__iregex=search_pattern)
        )

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    try:
        if price_min:
            products = products.filter(price__gte=Decimal(price_min))
    except (InvalidOperation, TypeError, ValueError):
        pass
    try:
        if price_max:
            products = products.filter(price__lte=Decimal(price_max))
    except (InvalidOperation, TypeError, ValueError):
        pass

    sort = request.GET.get('sort')
    if sort == 'price-asc':
        products = products.order_by('price')
    elif sort == 'price-desc':
        products = products.order_by('-price')
    elif sort == 'new':
        products = products.order_by('-created')

    return products


def catalog(request):
    """Полная страница — первая загрузка."""
    products = get_filtered_products(request)
    search_query = request.GET.get('q', '').strip()[:100]
    categories = Category.objects.all()
    total_count = Product.objects.filter(available=True).count()

    #ДОБАВИЛ ПАГИНАЦИЮ
    paginator = Paginator(products, 8) # 8 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,  #  ПЕРЕДАЕМ page_obj, а не products
        'categories': categories,
        'total_count': total_count,
        'page_obj': page_obj,  #  ПЕРЕДАЕМ для кнопок пагинации
        'search_query': search_query,
    }

    return render(request, 'main/catalog.html', context)


def catalog_ajax(request):
    products = get_filtered_products(request)
    search_query = request.GET.get('q', '').strip()[:100]
    
    # Пагинация
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Рендерим два HTML-куска отдельно
    products_html = render_to_string(
        'main/includes/product_list.html',
        {'products': page_obj, 'search_query': search_query},
        request=request,
    )
    pagination_html = render_to_string('main/includes/pagination.html', {'page_obj': page_obj}, request=request)
    
    # Возвращаем их в JSON
    return JsonResponse({
        'products_html': products_html,
        'pagination_html': pagination_html,
        'result_count': paginator.count,
        'search_query': search_query,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)

    # Похожие — та же категория, не считая текущий
    related_products = Product.objects.filter(
        category=product.category,
        available=True
    ).exclude(id=product.id)[:4]

    return render(request, 'main/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

def about(request):
    return render(request, 'main/about.html')


def privacy_policy(request):
    return render(request, 'main/privacy_policy.html')



def contacts(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняет в базу
            messages.success(request, 'Ваше сообщение отправлено!')
            return redirect('main:contacts')  # PRG-паттерн: после POST делаем GET
    else:
        form = ContactForm()  # Пустая форма для GET-запроса

    return render(request, 'main/contacts.html', {'form': form})

@require_POST
@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        # Если уже было в избранном — удаляем
        favorite.delete()
        status = 'removed'
    else:
        status = 'added'

    return JsonResponse({'status': status})

@login_required
def favorites_list(request):
    """Страница со списком избранных товаров"""
    # Получаем все записи Favorite для текущего пользователя
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    
    # Извлекаем сами объекты товаров, чтобы передать в шаблон
    products = [fav.product for fav in favorites]
    
    return render(request, 'main/favorites.html', {'products': products})

@login_required
def profile_edit(request):
    # Если у старого пользователя нет профиля — создаем ему пустой
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        # Ловим данные из формы
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        # Если обе формы валидны — сохраняем
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваши данные успешно обновлены!')
            return redirect('users:profile_edit')
    else:
        # Если это просто заход на страницу (GET) — заполняем форму текущими данными
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile_edit.html', context)
