from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_('E-mail'), 
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Seu e-mail'})
    )
    nome = forms.CharField(
        label=_('Nome completo'), 
        max_length=150, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Seu nome completo'})
    )
    password1 = forms.CharField(
        label=_('Senha'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Sua senha'})
    )
    password2 = forms.CharField(
        label=_('Confirme a senha'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirme sua senha'})
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'nome', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Usando email como username
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label=_('E-mail'), 
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'class': 'form-control form-control-lg',
            'placeholder': 'Seu e-mail'
        })
    )
    password = forms.CharField(
        label=_('Senha'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Sua senha',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        label=_('Lembrar-me'),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    error_messages = {
        'invalid_login': _('E-mail ou senha inválidos.'),
        'inactive': _('Esta conta está inativa. Por favor, verifique seu e-mail para ativá-la.'),
    }

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_('E-mail'), max_length=254)

class CustomSetPasswordForm(SetPasswordForm):
    pass

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nome']
        labels = {'nome': _('Nome completo')}
