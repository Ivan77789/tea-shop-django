from django.conf import settings

from main.models import Product

MAX_CART_QUANTITY = 99


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError('Количество должно быть положительным целым числом.')

        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}
        
        new_quantity = quantity if update_quantity else self.cart[product_id]['quantity'] + quantity
        if new_quantity > MAX_CART_QUANTITY:
            raise ValueError(f'Максимальное количество одного товара — {MAX_CART_QUANTITY}.')
        self.cart[product_id]['quantity'] = new_quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        products = self._available_products()
        for product_id, product in products.items():
            item = self.cart[product_id].copy()
            item['product'] = product
            item['price'] = product.price
            item['total_price'] = product.price * item['quantity']
            yield item

    def _available_products(self):
        products = {
            str(product.id): product
            for product in Product.objects.filter(id__in=self.cart, available=True)
        }
        stale_ids = self.cart.keys() - products.keys()
        if stale_ids:
            for product_id in stale_ids:
                del self.cart[product_id]
            self.save()
        return products

    def __len__(self):
        self._available_products()
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        products = self._available_products()
        return sum(products[product_id].price * item['quantity'] for product_id, item in self.cart.items())

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.cart = self.session[settings.CART_SESSION_ID]
        self.save()
