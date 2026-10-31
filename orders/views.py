from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from django.shortcuts import redirect, render

from cart.cart import Cart
from main.models import Product
from .forms import OrderCreateForm
from .models import Order, OrderItem
from .promos import NEWSLETTER_PROMO_CODE, calculate_promo_discount, get_first_order_promo


@require_POST
def promo_validate(request):
    email = request.POST.get('email', '').strip().lower()
    code = request.POST.get('promo_code', '').strip()
    subscription, error = get_first_order_promo(email, code)
    if error:
        return JsonResponse({'valid': False, 'message': error}, status=400)
    cart = Cart(request)
    if len(cart) == 0:
        return JsonResponse({'valid': False, 'message': 'Корзина пуста.'}, status=400)
    subtotal = cart.get_total_price()
    discount = calculate_promo_discount(subtotal)
    return JsonResponse({
        'valid': True,
        'message': 'Скидка 10% применена.',
        'discount': str(discount),
        'total': str(max(subtotal - discount, 0)),
        'promo_code': NEWSLETTER_PROMO_CODE,
    })

def order_create(request):
    cart = Cart(request)
    
    # Если корзина пуста — не пускаем
    if len(cart) == 0:
        return redirect('main:catalog')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            items = list(cart)
            if not items:
                return redirect('main:catalog')

            product_ids = [item['product'].id for item in items]
            try:
                with transaction.atomic():
                    locked_products = {
                        product.id: product
                        for product in Product.objects.select_for_update().filter(
                            id__in=product_ids,
                            available=True,
                        )
                    }

                    for item in items:
                        product = locked_products.get(item['product'].id)
                        if product is None:
                            raise ValueError(f'Товар «{item["product"].name}» больше недоступен.')
                        quantity = item['quantity']
                        mode, pack_weight = Cart.parse_mode(item['sale_mode'])
                        if mode == 'cake':
                            if not product.whole_cake_weight_grams:
                                raise ValueError(f'Продажа целым блином для «{product.name}» недоступна.')
                            if quantity > product.whole_cake_stock:
                                raise ValueError(
                                    f'«{product.name}»: осталось {product.whole_cake_stock} целых блинов.'
                                )
                        elif mode == Product.SALE_UNIT_GRAM:
                            if product.sale_unit != mode or quantity < 1 or pack_weight is None:
                                raise ValueError(
                                    f'Количество товара «{product.name}» изменилось. '
                                    'Обновите корзину и добавьте товар заново.'
                                )
                            total_weight = quantity * pack_weight
                            if not product.can_supply_grams(total_weight):
                                raise ValueError(
                                    f'Товара «{product.name}» осталось только '
                                    f'{product.available_grams} г.'
                                )
                        elif mode == 'trial':
                            if product.sale_unit != Product.SALE_UNIT_PIECE or quantity < 1:
                                raise ValueError(f'Пробник товара «{product.name}» больше недоступен.')
                            if product.trial_price is None:
                                raise ValueError(f'Пробник товара «{product.name}» не продаётся.')
                            if product.trial_stock_available is not None and quantity > product.trial_stock_available:
                                raise ValueError(
                                    f'«{product.name}»: осталось только {product.trial_stock_available} пакетиков.'
                                )
                        elif mode == Product.SALE_UNIT_PORTION:
                            if (
                                product.sale_unit != Product.SALE_UNIT_PORTION
                                or not product.portion_weight_grams
                                or quantity < 1
                            ):
                                raise ValueError(f'Порции товара «{product.name}» больше недоступны.')
                            available_portions = product.portion_stock_available
                            if available_portions is not None and quantity > available_portions:
                                raise ValueError(
                                    f'«{product.name}»: осталось только {available_portions} порций.'
                                )
                        elif mode == Product.SALE_UNIT_PIECE:
                            if product.sale_unit != mode or quantity < 1:
                                raise ValueError(f'Количество товара «{product.name}» изменилось.')
                            if product.stock_quantity is not None and quantity > product.stock_quantity:
                                available_boxes = product.stock_quantity
                                raise ValueError(f'«{product.name}»: осталось {available_boxes} коробок.')
                        else:
                            raise ValueError(f'Неизвестный формат продажи товара «{product.name}».')

                    promo_subscription = None
                    promo_code = form.cleaned_data.get('promo_code', '').strip()
                    if promo_code:
                        promo_subscription, promo_error = get_first_order_promo(
                            form.cleaned_data['email'].strip().lower(), promo_code, lock=True
                        )
                        if promo_error:
                            raise ValueError(promo_error)

                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
                    order.promo_code = NEWSLETTER_PROMO_CODE if promo_subscription else ''
                    order.save()

                    for item in items:
                        product = locked_products[item['product'].id]
                        mode, pack_weight = Cart.parse_mode(item['sale_mode'])
                        if mode == 'cake':
                            product.whole_cake_stock -= item['quantity']
                            product.save(update_fields=['whole_cake_stock'])
                            order_price = product.whole_cake_price
                            stock_deducted = True
                            order_quantity = item['quantity']
                            discount_percent = 0
                            stock_units_deducted = 0
                        elif mode == Product.SALE_UNIT_GRAM:
                            order_quantity = item['weight_grams']
                            discount_percent = max(product.discount_percent, product.discount_for_weight(pack_weight))
                            stock_deducted = product.stock_quantity is not None
                            if stock_deducted:
                                product.consume_gram_stock(order_quantity)
                                product.save(update_fields=['stock_quantity', 'whole_cake_stock'])
                            order_price = product.price
                            stock_units_deducted = order_quantity if stock_deducted else 0
                        elif mode == 'trial':
                            order_quantity = item['quantity']
                            discount_percent = 0
                            stock_deducted = product.stock_quantity is not None
                            if product.stock_quantity is not None:
                                product.consume_trial_packs(order_quantity)
                                product.save(update_fields=['stock_quantity', 'loose_pack_stock'])
                            order_price = product.trial_price
                            stock_units_deducted = order_quantity if product.stock_quantity is not None else 0
                        elif mode == Product.SALE_UNIT_PORTION:
                            order_quantity = item['quantity']
                            discount_percent = product.discount_percent
                            stock_deducted = product.stock_quantity is not None
                            stock_units_deducted = order_quantity * product.portion_weight_grams if stock_deducted else 0
                            if stock_deducted:
                                product.stock_quantity -= stock_units_deducted
                                product.save(update_fields=['stock_quantity'])
                            order_price = product.price
                        else:
                            order_quantity = item['quantity']
                            discount_percent = product.discount_percent if mode != 'trial' else 0
                            stock_deducted = product.stock_quantity is not None
                            stock_units_deducted = order_quantity if stock_deducted else 0
                            if stock_deducted:
                                product.stock_quantity -= order_quantity
                                product.save(update_fields=['stock_quantity'])
                            order_price = product.price
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=order_price,
                            quantity=order_quantity,
                            unit=(
                                OrderItem.UNIT_TRIAL if mode == 'trial'
                                else (
                                    Product.SALE_UNIT_GRAM if mode == Product.SALE_UNIT_GRAM
                                    else (
                                        OrderItem.UNIT_BOX if mode == Product.SALE_UNIT_PIECE
                                        else (OrderItem.UNIT_PORTION if mode == Product.SALE_UNIT_PORTION else mode)
                                    )
                                )
                            ),
                            discount_percent=discount_percent,
                            stock_deducted=stock_deducted,
                            stock_units_deducted=stock_units_deducted,
                        )
                    if promo_subscription:
                        order.promo_discount_amount = calculate_promo_discount(order.get_items_subtotal())
                        order.save(update_fields=['promo_discount_amount'])
                        promo_subscription.promo_used_at = timezone.now()
                        promo_subscription.save(update_fields=['promo_used_at'])
            except ValueError as error:
                form.add_error(None, str(error))
            else:
                cart.clear()
                return render(request, 'orders/order_created.html', {'order': order})
            
    else:
        # --- АВТОПОДСТАНОВКА ДАННЫХ ---
        initial_data = {}
        
        if request.user.is_authenticated:
            # Берем базовые данные пользователя
            initial_data['first_name'] = request.user.first_name
            initial_data['last_name'] = request.user.last_name
            initial_data['email'] = request.user.email
            
            # Берем данные из профиля (телефон, город, адрес)
            if hasattr(request.user, 'profile'):
                initial_data['phone'] = request.user.profile.phone
                initial_data['city'] = request.user.profile.default_city
                initial_data['address'] = request.user.profile.default_address

        # Передаем эти данные в форму. Django сам заполнит поля.
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})
