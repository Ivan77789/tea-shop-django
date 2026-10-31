from django.conf import settings

from main.models import Product

MAX_CART_QUANTITY = 99
MAX_CART_WEIGHT_GRAMS = 100000
GRAM_OPTIONS = (8, 25, 50, 100)


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(settings.CART_SESSION_ID)
        if self.cart is None:
            self.cart = self.session[settings.CART_SESSION_ID] = {}
        self._upgrade_legacy_keys()

    @staticmethod
    def key(product_id, sale_mode):
        return f'{product_id}:{sale_mode}'

    @staticmethod
    def parse_mode(mode):
        if mode.startswith('gram-'):
            try:
                weight = int(mode.split('-', 1)[1])
            except (TypeError, ValueError):
                return None, None
            return ('gram', weight) if weight in GRAM_OPTIONS else (None, None)
        if mode == 'gram':
            return 'gram', 50
        if mode in ('piece', 'cake'):
            return mode, None
        if mode == 'piece-box':
            return 'piece', None
        if mode == 'piece-trial':
            return 'trial', None
        if mode == Product.SALE_UNIT_PORTION:
            return Product.SALE_UNIT_PORTION, None
        return None, None

    def _upgrade_legacy_keys(self):
        legacy = [key for key in self.cart if ':' not in str(key) or str(key).endswith(':gram')]
        if not legacy:
            return
        product_ids = [str(key).split(':', 1)[0] for key in legacy]
        products = {
            str(product.id): product
            for product in Product.objects.filter(id__in=product_ids)
        }
        for old_key in legacy:
            old_key = str(old_key)
            product_id = old_key.split(':', 1)[0]
            product = products.get(product_id)
            old_item = self.cart.pop(old_key, {})
            if product is None:
                continue
            old_mode = old_key.split(':', 1)[1] if ':' in old_key else product.sale_unit
            quantity = int(old_item.get('quantity', 0) or 0)
            if old_mode == 'gram':
                # Older carts stored grams directly in 50 g increments.
                mode = 'gram-50'
                quantity = quantity // 50
            else:
                mode = old_mode
            self.cart[self.key(product_id, mode)] = {'quantity': quantity}
        self.save()

    def add(self, product, quantity=1, update_quantity=False, sale_mode=None):
        sale_mode = sale_mode or product.default_sale_mode
        if sale_mode == 'gram':
            sale_mode = 'gram-50'
        mode, pack_weight = self.parse_mode(sale_mode)
        if mode is None:
            raise ValueError('Неизвестный размер порции.')
        if mode == 'cake' and not product.whole_cake_weight_grams:
            raise ValueError('Для товара не задан вес целого блина.')
        if mode in ('piece', 'trial') and product.sale_unit != Product.SALE_UNIT_PIECE:
            raise ValueError('Этот товар продаётся на развес.')
        if mode == 'trial' and product.trial_price is None:
            raise ValueError('Пробник для этого товара не продаётся.')
        if mode == Product.SALE_UNIT_PORTION and (
            product.sale_unit != Product.SALE_UNIT_PORTION or not product.portion_weight_grams
        ):
            raise ValueError('Для порции не задан вес или товар продаётся в другом формате.')
        if mode == 'gram' and product.sale_unit != Product.SALE_UNIT_GRAM:
            raise ValueError('Этот товар продаётся поштучно.')
        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError('Укажите положительное целое количество.')

        item_key = self.key(product.id, sale_mode)
        current_quantity = self.cart.get(item_key, {}).get('quantity', 0)
        new_quantity = quantity if update_quantity else current_quantity + quantity

        if mode == 'gram':
            weight_grams = new_quantity * pack_weight
            if weight_grams > MAX_CART_WEIGHT_GRAMS:
                raise ValueError('Максимум для одного заказа — 100 кг развесного чая.')
            if not product.can_supply_grams(weight_grams):
                raise ValueError(f'В наличии только {product.available_grams} г')
        elif mode == 'cake':
            if new_quantity > MAX_CART_QUANTITY:
                raise ValueError(f'Максимальное количество — {MAX_CART_QUANTITY} блинов.')
            if new_quantity > product.whole_cake_stock:
                raise ValueError(f'В наличии только {product.whole_cake_stock} целых блинов.')
        elif mode == 'trial':
            if new_quantity > MAX_CART_QUANTITY:
                raise ValueError(f'Максимальное количество пробников — {MAX_CART_QUANTITY} шт.')
            if product.trial_stock_available is not None and new_quantity > product.trial_stock_available:
                raise ValueError(f'В наличии только {product.trial_stock_available} пакетиков.')
        elif mode == Product.SALE_UNIT_PORTION:
            if new_quantity > MAX_CART_QUANTITY:
                raise ValueError(f'Максимальное количество порций — {MAX_CART_QUANTITY} шт.')
            available_portions = product.portion_stock_available
            if available_portions is not None and new_quantity > available_portions:
                raise ValueError(f'В наличии только {available_portions} порций.')
        else:
            if new_quantity > MAX_CART_QUANTITY:
                raise ValueError(f'Максимальное количество товара — {MAX_CART_QUANTITY} шт.')
            if product.stock_quantity is not None and new_quantity > product.stock_quantity:
                available_boxes = product.stock_quantity
                raise ValueError(f'В наличии только {available_boxes} коробок.')

        self.cart[item_key] = {'quantity': new_quantity}
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product, sale_mode=None):
        sale_mode = sale_mode or product.default_sale_mode
        if sale_mode == 'gram':
            sale_mode = 'gram-50'
        item_key = self.key(product.id, sale_mode)
        if item_key in self.cart:
            del self.cart[item_key]
            self.save()

    def __iter__(self):
        products = self._available_products()
        for item_key, product in products.items():
            item = self.cart[item_key].copy()
            sale_mode = item_key.rsplit(':', 1)[1]
            mode, pack_weight = self.parse_mode(sale_mode)
            item.update(
                product=product,
                sale_mode=sale_mode,
                key=item_key,
                dom_id=f'{product.id}-{sale_mode}',
            )
            if mode == 'cake':
                item['price'] = product.whole_cake_price
                item['regular_price'] = product.whole_cake_regular_price
                item['discount_percent'] = product.whole_cake_discount_percent
                item['unit_label'] = f'целый блин ({product.whole_cake_weight_grams} г)'
                item['display_quantity'] = f'{item["quantity"]} × {item["unit_label"]}'
                item['price_unit_label'] = 'за целый блин'
                item['total_price'] = product.whole_cake_price * item['quantity']
                item['weight_grams'] = product.whole_cake_weight_grams * item['quantity']
                item['discount_savings'] = (
                    product.whole_cake_regular_price - product.whole_cake_price
                ) * item['quantity']
            elif mode == 'gram':
                item['weight_grams'] = pack_weight * item['quantity']
                item['discount_percent'] = max(product.discount_percent, product.discount_for_weight(pack_weight))
                item['price'] = product.discounted_line_total(pack_weight, item['discount_percent'])
                item['regular_price'] = product.line_total(pack_weight)
                item['unit_label'] = f'уп. по {pack_weight} г'
                item['display_quantity'] = f'{item["quantity"]} × {pack_weight} г = {item["weight_grams"]} г'
                item['price_unit_label'] = f'за {pack_weight} г'
                item['total_price'] = product.discounted_line_total(
                    item['weight_grams'], item['discount_percent']
                )
                item['discount_savings'] = (
                    product.line_total(item['weight_grams']) - item['total_price']
                )
            elif mode == 'trial':
                item['weight_grams'] = 0
                item['price'] = product.trial_price
                item['regular_price'] = product.trial_price
                item['discount_percent'] = 0
                item['unit_label'] = 'пробник'
                item['display_quantity'] = f'{item["quantity"]} × пробник'
                item['price_unit_label'] = 'за пробник'
                item['total_price'] = product.trial_price * item['quantity']
                item['discount_savings'] = 0
            elif mode == Product.SALE_UNIT_PORTION:
                portion_weight = product.portion_weight_grams
                discount_percent = product.discount_percent
                item['weight_grams'] = portion_weight * item['quantity']
                item['price'] = product.price
                item['regular_price'] = product.price
                item['discount_percent'] = discount_percent
                item['unit_label'] = (
                    f'{portion_weight} г'
                    if product.slug == 'smola-shu-puera'
                    else f'коробка, {portion_weight} г'
                )
                item['display_quantity'] = f'{item["quantity"]} × {item["unit_label"]}'
                item['price_unit_label'] = (
                    f'за {portion_weight} г'
                    if product.slug == 'smola-shu-puera'
                    else 'за коробку'
                )
                item['total_price'] = product._price_after_discount(
                    product.price * item['quantity'], discount_percent
                )
                item['discount_savings'] = product.price * item['quantity'] - item['total_price']
            else:
                item['weight_grams'] = 0
                item['price'] = product.price
                item['regular_price'] = product.price
                discount_percent = product.discount_percent if mode != 'trial' else 0
                item['discount_percent'] = discount_percent
                item['unit_label'] = (
                    f'коробка — {product.box_pack_count} шт.'
                    if product.box_pack_count > 1 else 'упаковка'
                )
                item['display_quantity'] = f'{item["quantity"]} × {item["unit_label"]}'
                item['price_unit_label'] = f'за {item["unit_label"]}'
                item['total_price'] = product._price_after_discount(
                    product.price * item['quantity'], discount_percent
                )
                item['discount_savings'] = product.price * item['quantity'] - item['total_price']
            item['step'] = 1
            yield item

    def _available_products(self):
        keys = list(self.cart)
        product_ids = [key.rsplit(':', 1)[0] for key in keys if ':' in key]
        products_by_id = {
            str(product.id): product
            for product in Product.objects.filter(id__in=product_ids, available=True)
        }
        result = {}
        for item_key in keys:
            if ':' not in item_key:
                continue
            product_id, sale_mode = item_key.rsplit(':', 1)
            product = products_by_id.get(product_id)
            mode, _ = self.parse_mode(sale_mode)
            if product is None or mode is None or (mode == 'cake' and not product.whole_cake_weight_grams):
                del self.cart[item_key]
                self.save()
                continue
            result[item_key] = product
        return result

    def __len__(self):
        return sum(1 for _ in self)

    def get_total_price(self):
        return sum((item['total_price'] for item in self), start=0)

    def get_total_discount(self):
        return sum((item['discount_savings'] for item in self), start=0)

    def get_product_total(self, product_id, sale_mode=None):
        return next(
            (item['total_price'] for item in self
             if str(item['product'].id) == str(product_id)
             and (sale_mode is None or item['sale_mode'] == sale_mode)),
            0,
        )

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.cart = self.session[settings.CART_SESSION_ID]
        self.save()
