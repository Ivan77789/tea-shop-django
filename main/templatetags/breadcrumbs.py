from urllib.parse import urlencode

from django import template
from django.urls import reverse

register = template.Library()


def _item(label, url=None):
    return {"label": label, "url": url}


@register.inclusion_tag("includes/breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    if match is None:
        return {"items": []}

    namespace = match.namespace
    route_name = match.url_name
    home = _item("Главная", reverse("main:index"))
    items = []

    if namespace == "main":
        if route_name == "index":
            return {"items": []}

        if route_name == "catalog":
            items = [home, _item("Каталог", reverse("main:catalog"))]
            category_slug = request.GET.get("category")
            category = next(
                (
                    item
                    for item in context.get("categories", [])
                    if item.slug == category_slug
                ),
                None,
            )
            if category:
                items.append(_item(category.name))

        elif route_name == "product_detail":
            product = context.get("product")
            items = [home, _item("Каталог", reverse("main:catalog"))]
            if product:
                category = product.category
                category_url = (
                    f"{reverse('main:catalog')}?"
                    f"{urlencode({'category': category.slug})}"
                )
                items.append(_item(category.name, category_url))
                items.append(_item(product.name))
            else:
                items.append(_item("Товар"))

        else:
            page_names = {
                "about": "О нас",
                "contacts": "Контакты",
                "favorites": "Избранное",
            }
            page_name = page_names.get(route_name)
            if page_name:
                items = [home, _item(page_name)]

    elif namespace == "users":
        account_url = reverse("users:account")
        account_pages = {
            "account": ("Личный кабинет", None, None),
            "orders_list": ("Мои заказы", "Личный кабинет", account_url),
            "profile_edit": ("Мои данные", "Личный кабинет", account_url),
            "password_change": (
                "Сменить пароль",
                "Мои данные",
                reverse("users:profile_edit"),
            ),
            "address_list": ("Адреса доставки", "Личный кабинет", account_url),
        }
        page_names = {
            "login": "Вход",
            "register": "Регистрация",
            "favorites": "Избранное",
        }

        if route_name in account_pages:
            page_name, parent_name, parent_url = account_pages[route_name]
            items = [home]
            if parent_url:
                items.append(_item(parent_name, parent_url))
            items.append(_item(page_name))
        elif route_name in page_names:
            items = [home, _item(page_names[route_name])]

    elif namespace == "cart" and route_name == "cart_detail":
        items = [home, _item("Корзина")]

    elif namespace == "orders" and route_name == "order_create":
        items = [
            home,
            _item("Корзина", reverse("cart:cart_detail")),
            _item("Оформление заказа"),
        ]

    return {"items": items}
