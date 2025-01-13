document.addEventListener('DOMContentLoaded', async () => {
    const patientList = document.getElementById('patientList');
    const token = localStorage.getItem('clinicaToken');
  
    if (token) {
      // Obter lista de pacientes do backend via Electron
      const patients = await window.electron.getPatients(token);
  
      if (patients && patients.length) {
        patientList.innerHTML = patients.map(patient => 
          `<li>${patient.name} - ${patient.age} anos</li>`
        ).join('');
      } else {
        alert('Nenhum paciente encontrado.');
      }
    } else {
      alert('Você não está logado.');
      window.location.href = 'index.html';
    }
  });
  