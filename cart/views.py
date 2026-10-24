from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from main.models import Product

from .cart import Cart


def cart_detail(request):
    """Страница корзины"""
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    """AJAX: Добавление товара"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, available=True)
    try:
        quantity = int(request.POST.get('quantity', 1))
        cart.add(product=product, quantity=quantity, update_quantity=request.POST.get('update') == 'True')
    except (TypeError, ValueError) as error:
        return JsonResponse({'status': 'error', 'message': str(error)}, status=400)
    
    return JsonResponse({
        'status': 'ok',
        'cart_total_items': len(cart),
        'total_price': str(cart.get_total_price()),
        'product_total': str(cart.cart[str(product_id)]['quantity'] * product.price)
    })

@require_POST
def cart_remove(request, product_id):
    """AJAX: Удаление товара"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    return JsonResponse({
        'status': 'ok',
        'cart_total_items': len(cart),
        'total_price': str(cart.get_total_price())
    })



@require_POST
def cart_clear(request):
    """Полностью очищает корзину"""
    cart = Cart(request)
    cart.clear()
    return JsonResponse({
        'status': 'ok',
        'cart_total_items': 0,
        'total_price': '0'
    })
