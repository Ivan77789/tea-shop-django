from django.db import transaction

from django.shortcuts import redirect, render

from cart.cart import Cart
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

            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.user = request.user
                order.save()

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        product_name=item['product'].name,
                        price=item['price'],
                        quantity=item['quantity']
                    )
            
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
