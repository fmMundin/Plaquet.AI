import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

@pytest.mark.django_db
def test_register_and_login(client):
    # Cadastro
    response = client.post(reverse('accounts:register'), {
        'email': 'teste@exemplo.com',
        'nome': 'Usuário Teste',
        'password1': 'SenhaForte123',
        'password2': 'SenhaForte123',
    })
    assert response.status_code == 302
    user = User.objects.get(email='teste@exemplo.com')
    assert not user.is_active
    # Ativação simulada
    user.is_active = True
    user.email_confirmado = True
    user.save()
    # Login
    response = client.post(reverse('accounts:login'), {
        'username': 'teste@exemplo.com',
        'password': 'SenhaForte123',
    })
    assert response.status_code == 302
    assert response.url.startswith('/accounts/profile')
