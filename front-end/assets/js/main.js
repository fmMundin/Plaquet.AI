// Importação de módulos
import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'path';
import fetch from 'node-fetch';  // Importando fetch como ES module

// Função para criar a janela do aplicativo
function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,   // Desativa a integração com Node.js no renderizador
      contextIsolation: true,   // Habilita a separação de contextos
      preload: path.join(path.resolve(), 'assets/js/preload.js'),  // Caminho para o preload.js
    },
  });

  win.loadFile(path.join(path.resolve(), 'templates/login.html'));  // Caminho para o arquivo HTML
}

// Criação da janela quando o Electron estiver pronto
app.whenReady().then(createWindow);

// Manipuladores de eventos com ipcMain

// Função de login
ipcMain.handle('login', async (event, { email, password }) => {
  const response = await fetch('http://127.0.0.1:5000/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();
  return data;
});

// Função de cadastro
ipcMain.handle('register', async (event, { clinicaName, clinicaEmail, clinicaPassword }) => {
  const response = await fetch('http://127.0.0.1:5000/api/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: clinicaName,
      email: clinicaEmail,
      password: clinicaPassword,
    }),
  });

  const data = await response.json();
  return data;
});

// Função para listar pacientes
ipcMain.handle('getPatients', async (event, { token }) => {
  const response = await fetch('http://127.0.0.1:5000/api/patients', {
    headers: { 'Authorization': `Bearer ${token}` },
  });

  const data = await response.json();
  return data;
});
