document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
  
        // Enviar os dados de login para o backend via Electron
        const response = await window.electron.login(email, password);
  
        if (response.token) {
          localStorage.setItem('clinicaToken', response.token); // Armazenar o token
          window.location.href = 'pacientes.html'; // Redireciona para a tela de pacientes
        } else {
          alert(response.message || 'Erro ao fazer login.');
        }
      });
    }
  });
  