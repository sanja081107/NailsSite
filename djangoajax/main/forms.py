from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import *


class PostForm(ModelForm):
    title = forms.CharField(label='Название', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}))
    date = forms.DateTimeField(label='День для записи', required=True, widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Post
        fields = ('title', 'date', 'is_active')

    widgets = {
        'is_active': forms.CheckboxInput(attrs={'class': 'form-check'})
    }


class PostEditForm(ModelForm):
    title = forms.CharField(label='Название', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}))
    date = forms.DateTimeField(label='День для записи', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Post
        fields = ('title', 'client', 'service', 'date', 'is_active')
        widgets = {
            'client': forms.Select(attrs={
                'class': 'form-control',
            }),
            'service': forms.Select(attrs={
                'class': 'form-control',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check'}),
        }


class PostServiceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].empty_label = 'Все услуги'

    class Meta:
        model = Post
        fields = ('service',)
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class MyWorksCreateForm(ModelForm):
    title = forms.CharField(label='Имя фото', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: photo 1'}))
    photo = forms.ImageField(label='Фото работы', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'type': 'file', 'accept': 'image/*'}))
    date = forms.DateTimeField(label='Дата создания фото', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date', 'value': datetime.date(datetime.now())}))

    class Meta:
        model = MyWorks
        fields = ('title', 'photo', 'date', 'is_active')
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check'})
        }


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}))

    class Meta:
        model = User


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}))
    birthday = forms.DateTimeField(label='День рождения (не обязательно)', required=False, widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}))
    first_name = forms.CharField(label='Имя', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'}))
    last_name = forms.CharField(label='Фамилия', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите вашу фамилию'}))
    photo = forms.ImageField(label='Ваше фото (не обязательно)', required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'type': 'file', 'accept': 'image/*'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}))
    password2 = forms.CharField(label='Пароль повторно', widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль повторно'}))
    email = forms.CharField(label='Электронная почта', required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите электронную почту'}))
    mobile = forms.IntegerField(label='Номер телефона', required=True, widget=forms.TextInput(attrs={"type": "number", 'class': 'form-control', 'placeholder': 'Введите мобильный телефон'}))
    instagram = forms.CharField(label='Имя в инстаграм', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя в инстаграм'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'birthday', 'photo', 'email', 'mobile', 'instagram', 'password1', 'password2')

class UpdateUserForm(ModelForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}))
    birthday = forms.DateTimeField(label='День рождения (не обязательно)', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
    first_name = forms.CharField(label='Имя', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя'}))
    last_name = forms.CharField(label='Фамилия', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите вашу фамилию'}))
    photo = forms.ImageField(label='Ваше фото (не обязательно)', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'type': 'file', 'accept': 'image/*'}))
    email = forms.CharField(label='Электронная почта', required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите электронную почту'}))
    mobile = forms.IntegerField(label='Номер телефона', required=True, widget=forms.TextInput(attrs={"type": "number", 'class': 'form-control', 'placeholder': 'Пример: 375331234567'}))
    instagram = forms.CharField(label='Имя в инстаграм', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ваше имя в инстаграм'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'birthday', 'photo', 'email', 'mobile', 'instagram')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('birthday', 'photo', 'instagram', 'mobile')
