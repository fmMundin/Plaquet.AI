from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.conf import settings

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            # URLs que não precisam de autenticação
            allowed_paths = [
                reverse('accounts:login'),
                reverse('accounts:register'),
                reverse('accounts:password_reset'),
                reverse('accounts:password_reset_done'),
                '/admin/login/',
                '/static/',
                '/media/',
            ]
            
            # Verifica se a URL atual está na lista de permitidas
            current_path = request.path_info
            
            # Permite URLs de reset de senha
            if 'reset' in current_path and 'accounts' in current_path:
                return self.get_response(request)
                
            # Permite URLs na lista de permitidas
            if not any(current_path.startswith(path) for path in allowed_paths):
                return redirect('accounts:login')
        
        return self.get_response(request)
