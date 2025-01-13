document.addEventListener('DOMContentLoaded', () => {
    const cadastroForm = document.getElementById('cadastroForm');
  
    if (cadastroForm) {
      cadastroForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const clinicaName = document.getElementById('clinicaName').value;
        const clinicaEmail = document.getElementById('clinicaEmail').value;
        const clinicaPassword = document.getElementById('clinicaPassword').value;
  
        // Enviar dados de cadastro para o backend via Electron
        const response = await window.electron.register(clinicaName, clinicaEmail, clinicaPassword);
  
        if (response.message === 'Clinica cadastrada com sucesso!') {
          alert('Cadastro realizado com sucesso!');
          window.location.href = 'index.html'; // Redireciona para a tela de login
        } else {
          alert(response.message || 'Erro ao cadastrar.');
        }
      });
    }
  });
  