from django.db import transaction

from django.shortcuts import redirect, render

from cart.cart import Cart
from main.models import Product
from .forms import OrderCreateForm
from .models import OrderItem

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
                            if product.stock_quantity is not None and total_weight > product.stock_quantity:
                                unit_label = 'г' if mode == Product.SALE_UNIT_GRAM else 'шт.'
                                raise ValueError(
                                    f'Товара «{product.name}» осталось только '
                                    f'{product.stock_quantity} {unit_label}.'
                                )
                        elif mode == Product.SALE_UNIT_PIECE:
                            if product.sale_unit != mode or quantity < 1:
                                raise ValueError(f'Количество товара «{product.name}» изменилось.')
                            if product.stock_quantity is not None and quantity > product.stock_quantity:
                                raise ValueError(f'«{product.name}»: осталось {product.stock_quantity} шт.')
                        else:
                            raise ValueError(f'Неизвестный формат продажи товара «{product.name}».')

                    order = form.save(commit=False)
                    if request.user.is_authenticated:
                        order.user = request.user
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
                        elif mode == Product.SALE_UNIT_GRAM:
                            order_quantity = item['weight_grams']
                            discount_percent = product.discount_for_weight(pack_weight)
                            stock_deducted = product.stock_quantity is not None
                            if stock_deducted:
                                product.stock_quantity -= order_quantity
                                product.save(update_fields=['stock_quantity'])
                            order_price = product.price
                        else:
                            order_quantity = item['quantity']
                            discount_percent = 0
                            stock_deducted = product.stock_quantity is not None
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
                            unit=Product.SALE_UNIT_GRAM if mode == Product.SALE_UNIT_GRAM else mode,
                            discount_percent=discount_percent,
                            stock_deducted=stock_deducted,
                        )
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
