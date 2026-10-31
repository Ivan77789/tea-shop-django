from decimal import Decimal, ROUND_HALF_UP

from main.models import NewsletterSubscription

from .models import Order


NEWSLETTER_PROMO_CODE = 'TEA10'
NEWSLETTER_PROMO_PERCENT = 10


def get_first_order_promo(email, code, lock=False):
    """Return an eligible newsletter subscription or a user-facing error."""
    if (code or '').strip().upper() != NEWSLETTER_PROMO_CODE:
        return None, 'Промокод не распознан.'

    subscriptions = NewsletterSubscription.objects.filter(email__iexact=(email or '').strip())
    if lock:
        subscriptions = subscriptions.select_for_update()
    subscription = subscriptions.first()
    if subscription is None:
        return None, 'Подпишитесь на новости с этой электронной почты, чтобы получить скидку.'
    if subscription.promo_used_at:
        return None, 'Этот промокод уже использован.'
    if Order.objects.filter(email__iexact=(email or '').strip()).exists():
        return None, 'Скидка действует только на первый заказ.'
    return subscription, ''


def calculate_promo_discount(subtotal):
    return (subtotal * Decimal(NEWSLETTER_PROMO_PERCENT) / Decimal('100')).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
