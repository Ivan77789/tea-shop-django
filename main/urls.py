from django.urls import path

from main import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/ajax/', views.catalog_ajax, name='catalog_ajax'),   # ← новый
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('newsletter/subscribe/', views.newsletter_signup, name='newsletter_signup'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('favorite/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
]
