import re
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import ExpressionWrapper, F, IntegerField, Q, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from users.forms import ProfileUpdateForm, UserUpdateForm
from users.models import Profile

from .forms import ContactForm
from .models import Category, Favorite, NewsletterSubscription, Product


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

    if request.GET.get('only_discount') == '1':
        products = products.annotate(
            _sellable_grams=ExpressionWrapper(
                Coalesce(F('stock_quantity'), Value(0))
                + Coalesce(F('whole_cake_weight_grams'), Value(0)) * F('whole_cake_stock'),
                output_field=IntegerField(),
            )
        )
        discount_filter = (
            (Q(sale_unit=Product.SALE_UNIT_GRAM, discount_percent__gt=0)
             & (Q(stock_quantity__isnull=True) | Q(_sellable_grams__gte=8)))
            | (Q(sale_unit=Product.SALE_UNIT_GRAM, discount_8g_percent__gt=0)
               & (Q(stock_quantity__isnull=True) | Q(_sellable_grams__gte=8)))
            | (Q(sale_unit=Product.SALE_UNIT_GRAM, discount_25g_percent__gt=0)
               & (Q(stock_quantity__isnull=True) | Q(_sellable_grams__gte=25)))
            | (Q(sale_unit=Product.SALE_UNIT_GRAM, discount_50g_percent__gt=0)
               & (Q(stock_quantity__isnull=True) | Q(_sellable_grams__gte=50)))
            | (Q(sale_unit=Product.SALE_UNIT_GRAM, discount_100g_percent__gt=0)
               & (Q(stock_quantity__isnull=True) | Q(_sellable_grams__gte=100)))
            | Q(sale_unit=Product.SALE_UNIT_GRAM, whole_cake_discount_percent__gt=0,
                whole_cake_weight_grams__gt=0, whole_cake_stock__gt=0)
            | (Q(discount_percent__gt=0) & ~Q(sale_unit=Product.SALE_UNIT_GRAM))
        )
        products = products.filter(discount_filter)

    if request.GET.get('only_new') == '1':
        products = products.filter(is_new=True)

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
    query_params = request.GET.copy()
    query_params.pop('page', None)

    context = {
        'products': page_obj,  #  ПЕРЕДАЕМ page_obj, а не products
        'categories': categories,
        'total_count': total_count,
        'page_obj': page_obj,  #  ПЕРЕДАЕМ для кнопок пагинации
        'search_query': search_query,
        'query_params': query_params.urlencode(),
    }

    return render(request, 'main/catalog.html', context)


def catalog_ajax(request):
    products = get_filtered_products(request)
    search_query = request.GET.get('q', '').strip()[:100]
    
    # Пагинация
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    query_params.pop('page', None)
    
    # Рендерим два HTML-куска отдельно
    products_html = render_to_string(
        'main/includes/product_list.html',
        {'products': page_obj, 'search_query': search_query},
        request=request,
    )
    pagination_html = render_to_string(
        'main/includes/pagination.html',
        {'page_obj': page_obj, 'query_params': query_params.urlencode()},
        request=request,
    )
    
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


@require_POST
def newsletter_signup(request):
    email = request.POST.get('email', '').strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'ok': False, 'message': 'Введите корректный адрес электронной почты.'}, status=400)

    subscription, _ = NewsletterSubscription.objects.get_or_create(email=email)
    if subscription.promo_sent_at:
        return JsonResponse({'ok': True, 'message': 'Промокод уже отправляли на эту почту. Проверьте входящие и папку «Спам».'})

    if (
        settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend'
        or not settings.EMAIL_HOST
        or not settings.DEFAULT_FROM_EMAIL
    ):
        return JsonResponse({
            'ok': False,
            'message': 'Отправка почты ещё не настроена. Адрес сохранён, попробуйте позже.',
        }, status=503)

    try:
        with transaction.atomic():
            subscription = NewsletterSubscription.objects.select_for_update().get(pk=subscription.pk)
            if subscription.promo_sent_at:
                return JsonResponse({'ok': True, 'message': 'Промокод уже отправляли на эту почту. Проверьте входящие и папку «Спам».'})
            sent = send_mail(
                'Ваш промокод на первый заказ',
                'Спасибо за подписку на новости «Чай из Китая»! Ваш промокод TEA10 даёт скидку 10% на первый заказ. Введите его при оформлении заказа с этого адреса электронной почты.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            if not sent:
                raise RuntimeError('Почтовый сервер не принял письмо.')
            subscription.promo_sent_at = timezone.now()
            subscription.save(update_fields=['promo_sent_at'])
    except Exception:
        return JsonResponse({
            'ok': False,
            'message': 'Не удалось отправить письмо. Проверьте настройки почты и попробуйте ещё раз.',
        }, status=503)

    return JsonResponse({'ok': True, 'message': 'Промокод отправлен на почту. Проверьте входящие и папку «Спам».'})



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
