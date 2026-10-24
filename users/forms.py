from django import forms
from django.core.exceptions import ValidationError
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

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

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

    def clean(self):
        username = self.cleaned_data.get('username')
        if username and '@' in username:
            matching_usernames = list(
                User.objects.filter(email__iexact=username).values_list('username', flat=True)[:2]
            )
            if len(matching_usernames) == 1:
                self.cleaned_data['username'] = matching_usernames[0]
            elif len(matching_usernames) > 1:
                self.cleaned_data['username'] = ''
        return super().clean()





class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email'] # ТОЛЬКО поля из модели User
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'Имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'example@mail.com'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Этот email уже используется другим аккаунтом.')
        return email

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile # Здесь мы указываем модель Profile
        fields = ['avatar', 'phone', 'default_city', 'default_address', 'subscribe_news']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-input profile-edit__avatar-input',
                'accept': 'image/*',
            }),
            'phone': forms.TextInput(attrs={'class': 'form-input input-with-icon', 'placeholder': '+380...'}),
            'default_city': forms.TextInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'Киев'}),
            'default_address': forms.TextInput(attrs={'class': 'form-input input-with-icon', 'placeholder': 'Улица, дом, квартира'}),
            'subscribe_news': forms.CheckboxInput(attrs={'class': 'switch-input'}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and avatar.size > 5 * 1024 * 1024:
            raise ValidationError('Размер изображения не должен превышать 5 МБ.')
        return avatar
