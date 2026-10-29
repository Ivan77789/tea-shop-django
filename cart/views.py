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
        sale_mode = request.POST.get('sale_mode') or product.default_sale_mode
        if sale_mode == 'gram':
            sale_mode = 'gram-50'
        cart.add(
            product=product,
            quantity=quantity,
            sale_mode=sale_mode,
            update_quantity=request.POST.get('update') == 'True',
        )
    except (TypeError, ValueError) as error:
        return JsonResponse({'status': 'error', 'message': str(error)}, status=400)
    
    return JsonResponse({
        'status': 'ok',
        'cart_total_items': len(cart),
        'total_price': str(cart.get_total_price()),
        'total_discount': str(cart.get_total_discount()),
        'product_total': str(cart.get_product_total(product_id, sale_mode)),
        'sale_mode': sale_mode,
    })

@require_POST
def cart_remove(request, product_id):
    """AJAX: Удаление товара"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    sale_mode = request.POST.get('sale_mode') or product.default_sale_mode
    cart.remove(product, sale_mode)
    
    return JsonResponse({
        'status': 'ok',
        'cart_total_items': len(cart),
        'total_price': str(cart.get_total_price()),
        'total_discount': str(cart.get_total_discount()),
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
