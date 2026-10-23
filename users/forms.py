from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


# Форма регистрации
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'example@mail.com'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'Введите ваше имя'}))

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

    # Переопределяем виджеты (стили) для стандартных полей
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input input-with-icon', 'placeholder': 'Придумайте логин'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input input-with-icon', 'placeholder': 'Придумайте пароль'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input input-with-icon', 'placeholder': 'Повторите пароль'})

# Форма входа
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input input-with-icon', 'placeholder': 'Ваш логин или email'})
        self.fields['password'].widget.attrs.update({'class': 'form-input input-with-icon', 'placeholder': 'Введите пароль'})





class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email'] # ТОЛЬКО поля из модели User
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'Имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'example@mail.com'}),
        }
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile # Здесь мы указываем модель Profile
        fields = ['phone', 'default_city', 'default_address', 'subscribe_news'] # Поля из Profile
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input input-with-icon', 'placeholder': '+380...'}),
            'default_city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Киев'}),
            'default_address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Улица, дом, квартира'}),
            'subscribe_news': forms.CheckboxInput(attrs={'class': 'switch-input'}),
        }