from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileEditForm
from .models import CustomUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponse

# Proteção brute force (django-axes)
# Basta instalar e adicionar no settings.py

# Login personalizado
from django.contrib.auth.signals import user_login_failed
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('Analises:index')
    
    form = CustomAuthenticationForm()
    
    if request.method == 'POST':
        ip = get_client_ip(request)
        attempt_key = f'login_attempt_{ip}'
        block_key = f'login_block_{ip}'
        
        # Verifica se o IP está bloqueado
        if cache.get(block_key):
            messages.error(request, _('Muitas tentativas de login. Tente novamente em 1 hora.'))
            return redirect('accounts:locked')
        
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # Login bem-sucedido - limpa contadores
                cache.delete(attempt_key)
                cache.delete(block_key)
                
                login(request, user)
                if form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(1209600)  # 2 semanas
                else:
                    request.session.set_expiry(0)  # Até fechar o navegador
                    
                next_url = request.GET.get('next')
                if next_url and not next_url.startswith('/accounts/login'):
                    return redirect(next_url)
                return redirect('Analises:index')
            else:
                # Incrementa contador de tentativas
                attempts = cache.get(attempt_key, 0) + 1
                cache.set(attempt_key, attempts, 300)  # Expira em 5 minutos
                
                # Bloqueia após 5 tentativas
                if attempts >= 5:
                    cache.set(block_key, True, 3600)  # Bloqueia por 1 hora
                    messages.error(request, _('Muitas tentativas de login. Tente novamente em 1 hora.'))
                    return redirect('accounts:locked')
                    
                messages.error(request, _('E-mail ou senha inválidos.'))
        else:
            messages.error(request, _('Por favor, corrija os erros abaixo.'))
    
    return render(request, 'accounts/login.html', {'form': form, 'login': True})

def custom_logout(request):
    logout(request)
    messages.success(request, _('Logout realizado com sucesso.'))
    return redirect('accounts:login')

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = True  # Ativa direto para dev
                user.email_confirmado = True
                user.save()
                messages.success(request, _('Cadastro realizado com sucesso! Você já pode fazer login.'))
                
                # Fazer login automático após o registro
                login(request, user)
                return redirect('Analises:analises')
            except Exception as e:
                messages.error(request, _('Erro ao criar conta. Por favor, tente novamente.'))
        else:
            if CustomUser.objects.filter(email=request.POST.get('email')).exists():
                messages.error(request, _('Já existe uma conta com este e-mail.'))
            else:
                for field in form:
                    for error in field.errors:
                        messages.error(request, f"{field.label}: {error}")
    
    return render(request, 'accounts/register.html', {'form': form})

def send_email_confirmation(request, user):
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from django.contrib.auth.tokens import default_token_generator
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = request.build_absolute_uri(reverse('accounts:email_confirm', args=[uid, token]))
    subject = _('Confirmação de e-mail')
    message = render_to_string('accounts/email_confirm.html', {'user': user, 'url': url})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def email_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user and default_token_generator.check_token(user, token):
        user.email_confirmado = True
        user.is_active = True
        user.save()
        messages.success(request, _('E-mail confirmado com sucesso!'))
        return redirect('accounts:email_confirm_complete')
    else:
        messages.error(request, _('Link de confirmação inválido ou expirado.'))
        return redirect('accounts:login')

def email_confirm_sent(request):
    return render(request, 'accounts/email_confirm_sent.html')

def email_confirm_complete(request):
    return render(request, 'accounts/email_confirm_complete.html')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Perfil atualizado com sucesso.'))
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})
