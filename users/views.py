import logging
from datetime import timedelta

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core import signing
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from main.models import Favorite
from orders.models import Order  # Проверь, что импортировано

from .forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
    ProfileUpdateForm,
    UserUpdateForm,
)
from .models import Profile

logger = logging.getLogger(__name__)
EMAIL_CONFIRMATION_MAX_AGE = 60 * 60 * 24 * 3
EMAIL_RESEND_COOLDOWN = timedelta(minutes=1)


def _send_confirmation_email(request, *, user, email, purpose):
    if purpose == 'signup':
        route_name = 'users:verify_email'
        subject = 'Подтвердите адрес электронной почты'
        salt = 'users.signup-email-confirmation'
        action = 'активировать аккаунт'
    else:
        route_name = 'users:confirm_email_change'
        subject = 'Подтвердите новый адрес электронной почты'
        salt = 'users.email-change-confirmation'
        action = 'подтвердить новый адрес'

    token = signing.dumps({'user_id': user.pk, 'email': email}, salt=salt)
    confirmation_url = request.build_absolute_uri(
        reverse(route_name, kwargs={'token': token})
    )
    send_mail(
        subject,
        f'Чтобы {action}, откройте ссылку и нажмите кнопку подтверждения:\n\n'
        f'{confirmation_url}\n\nСсылка действует 3 дня.',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def _load_confirmation_token(token, salt):
    try:
        return signing.loads(token, salt=salt, max_age=EMAIL_CONFIRMATION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def _confirmation_error(request):
    messages.error(request, 'Ссылка недействительна или срок её действия истёк.')
    return redirect('users:login')


# Вход
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True # Если уже вошел - на главную

# Регистрация
def register(request):
    if request.user.is_authenticated:
        return redirect('main:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            try:
                _send_confirmation_email(
                    request,
                    user=user,
                    email=user.email,
                    purpose='signup',
                )
            except Exception:
                logger.exception('Не удалось отправить письмо подтверждения регистрации.')
                user.delete()
                form.add_error(None, 'Не удалось отправить письмо. Проверьте настройки почты и попробуйте ещё раз.')
            else:
                profile = user.profile
                profile.email_verification_sent_at = timezone.now()
                profile.save(update_fields=['email_verification_sent_at'])
                return render(request, 'users/email_confirmation_sent.html', {
                    'email': user.email,
                    'purpose': 'signup',
                })
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def verify_email(request, token):
    payload = _load_confirmation_token(token, 'users.signup-email-confirmation')
    if not payload:
        return _confirmation_error(request)

    user = User.objects.filter(
        pk=payload.get('user_id'),
        email__iexact=payload.get('email', ''),
    ).first()
    if user is None:
        return _confirmation_error(request)

    if request.method == 'POST':
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
        messages.success(request, 'Email подтверждён. Теперь вы можете войти.')
        return redirect('users:login')

    return render(request, 'users/confirm_email.html', {'purpose': 'signup'})


@require_http_methods(['GET', 'POST'])
def confirm_email_change(request, token):
    payload = _load_confirmation_token(token, 'users.email-change-confirmation')
    if not payload:
        return _confirmation_error(request)

    user = User.objects.filter(pk=payload.get('user_id')).first()
    if user is None:
        return _confirmation_error(request)

    profile = Profile.objects.filter(user=user).first()
    if profile is None or profile.pending_email.casefold() != str(payload.get('email', '')).casefold():
        return _confirmation_error(request)

    if request.method == 'POST':
        if User.objects.filter(email__iexact=profile.pending_email).exclude(pk=user.pk).exists():
            profile.pending_email = ''
            profile.save(update_fields=['pending_email'])
            messages.error(request, 'Этот email уже используется другим аккаунтом.')
            return redirect('users:profile_edit')

        user.email = profile.pending_email
        user.save(update_fields=['email'])
        profile.pending_email = ''
        profile.save(update_fields=['pending_email'])
        messages.success(request, 'Новый email подтверждён и сохранён.')
        return redirect('users:profile_edit')

    return render(request, 'users/confirm_email.html', {'purpose': 'change'})


@require_POST
def resend_verification(request):
    email = request.POST.get('email', '').strip()
    user = User.objects.filter(email__iexact=email, is_active=False).first()

    if user is not None:
        profile, _ = Profile.objects.get_or_create(user=user)
        last_sent_at = profile.email_verification_sent_at
        if last_sent_at is None or timezone.now() - last_sent_at >= EMAIL_RESEND_COOLDOWN:
            try:
                _send_confirmation_email(
                    request,
                    user=user,
                    email=user.email,
                    purpose='signup',
                )
            except Exception:
                logger.exception('Не удалось повторно отправить письмо подтверждения.')
            else:
                profile.email_verification_sent_at = timezone.now()
                profile.save(update_fields=['email_verification_sent_at'])

    messages.info(request, 'Если для этого адреса есть неподтверждённый аккаунт, письмо отправлено.')
    return redirect('users:login')

# Выход
@require_POST
def logout_view(request):
    logout(request)
    return redirect('main:index')



@login_required
def account(request):
    Profile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'users/account.html', {
        'user': request.user,
        'orders': orders,
    })

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    # Получаем сами товары из избранного
    products = [fav.product for fav in favorites]
    return render(request, 'main/favorites.html', {'products': products})



@login_required
def orders_list(request):
    # Берем заказы только этого пользователя, сначала новые
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'users/orders_list.html', {'orders': orders})





@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        user_valid = u_form.is_valid()
        profile_valid = p_form.is_valid()
        if user_valid and profile_valid:
            requested_email = u_form.cleaned_data['email'].strip()
            email_changed = requested_email.casefold() != request.user.email.casefold()
            previous_avatar = profile.avatar
            updated_profile = p_form.save()
            u_form.save()

            if previous_avatar and previous_avatar.name != updated_profile.avatar.name:
                previous_avatar.delete(save=False)

            if email_changed:
                profile.pending_email = requested_email
                profile.save(update_fields=['pending_email'])
                last_sent_at = profile.email_verification_sent_at
                if last_sent_at is not None and timezone.now() - last_sent_at < EMAIL_RESEND_COOLDOWN:
                    messages.info(request, 'Новый email сохранён как ожидающий подтверждения. Повторно отправить письмо можно через минуту.')
                    return redirect('users:profile_edit')
                try:
                    _send_confirmation_email(
                        request,
                        user=request.user,
                        email=requested_email,
                        purpose='change',
                    )
                except Exception:
                    logger.exception('Не удалось отправить письмо подтверждения нового email.')
                    profile.pending_email = ''
                    profile.save(update_fields=['pending_email'])
                    messages.error(request, 'Не удалось отправить письмо подтверждения. Проверьте настройки почты и попробуйте снова.')
                else:
                    profile.email_verification_sent_at = timezone.now()
                    profile.save(update_fields=['email_verification_sent_at'])
                    messages.success(request, 'Письмо для подтверждения нового email отправлено. Адрес изменится после подтверждения.')
            else:
                messages.success(request, 'Ваши данные успешно обновлены!')
                if profile.pending_email:
                    profile.pending_email = ''
                    profile.save(update_fields=['pending_email'])
            return redirect('users:profile_edit')
    else:
        u_form = UserUpdateForm(
            instance=request.user,
            initial={'email': profile.pending_email or request.user.email},
        )
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'user': request.user,
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile,
        'google_connected': SocialAccount.objects.filter(
            user=request.user,
            provider='google',
        ).exists(),
    }
    return render(request, 'users/profile_edit.html', context)




@login_required
def address_list(request):
    # Пока просто отдаем шаблон-заглушку
    return render(request, 'users/address_list.html')
