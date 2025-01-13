document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            // Usar a API do preload para enviar os dados ao backend
            const response = await window.electronAPI.sendToBackend('http://127.0.0.1:5000/api/login', {
                email,
                password,
            });

            if (response.success) {
                alert('Login bem-sucedido!');
                window.location.href = 'patients.html'; // Redirecionar
            } else {
                alert('Credenciais inválidas.');
            }
        });
    }
});
