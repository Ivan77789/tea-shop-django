from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('confirm-email-change/<str:token>/', views.confirm_email_change, name='confirm_email_change'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account, name='account'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('orders/', views.orders_list, name='orders_list'),
    path('profile/', views.profile_edit, name='profile_edit'),
        path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html',
        success_url='/users/profile/' # Куда перекинуть после смены
    ), name='password_change'),
    path('addresses/', views.address_list, name='address_list'),
]
