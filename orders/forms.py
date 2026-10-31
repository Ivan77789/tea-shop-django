from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    promo_code = forms.CharField(
        required=False,
        max_length=30,
        label='Промокод',
        widget=forms.TextInput(attrs={
            'class': 'form-input', 'placeholder': 'Введите TEA10', 'autocomplete': 'off',
        }),
    )

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'address', 'comment', 'promo_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Введите имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Введите фамилию'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'example@mail.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+380...'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Киев'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Улица, дом, квартира'}),
            'comment': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Комментарий к заказу'}),
        }
