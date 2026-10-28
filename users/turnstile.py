import logging
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

SITEVERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'


def verify_turnstile_token(token, request, expected_action):
    site_key = settings.TURNSTILE_SITE_KEY
    secret_key = settings.TURNSTILE_SECRET_KEY
    if not site_key or not secret_key:
        raise ValidationError('Проверка безопасности не настроена. Попробуйте позже.')

    token = (token or '').strip()
    if not token or len(token) > 2048:
        raise ValidationError('Пройдите проверку безопасности и попробуйте ещё раз.')

    try:
        response = requests.post(
            SITEVERIFY_URL,
            data={'secret': secret_key, 'response': token},
            timeout=(3.05, 8),
        )
        response.raise_for_status()
        result = response.json()
    except (requests.RequestException, ValueError):
        logger.exception('Cloudflare Turnstile Siteverify request failed.')
        raise ValidationError('Не удалось выполнить проверку безопасности. Попробуйте ещё раз.')

    expected_host = urlsplit(f'//{request.get_host()}').hostname
    if (
        not isinstance(result, dict)
        or not result.get('success')
        or result.get('action') != expected_action
        or result.get('hostname', '').lower() != (expected_host or '').lower()
    ):
        raise ValidationError('Проверка безопасности не пройдена. Обновите страницу и попробуйте снова.')
