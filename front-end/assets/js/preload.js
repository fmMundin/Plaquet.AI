const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  login: async (email, password) => {
    return await ipcRenderer.invoke('login', { email, password });
  },
  register: async (clinicaName, clinicaEmail, clinicaPassword) => {
    return await ipcRenderer.invoke('register', { clinicaName, clinicaEmail, clinicaPassword });
  },
  getPatients: async (token) => {
    return await ipcRenderer.invoke('getPatients', { token });
  }
});
