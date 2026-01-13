const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Orb control methods
  initializeOrb: (workerId) => ipcRenderer.invoke('orb:initialize', workerId),
  getOrbPosition: () => ipcRenderer.invoke('orb:get-position'),
  assistWithTask: (task) => ipcRenderer.invoke('orb:assist', task),
  getScreenContext: () => ipcRenderer.invoke('orb:screen-context'),
  clickQuery: (x, y) => ipcRenderer.invoke('orb:click-query', x, y),
  requestPermissions: () => ipcRenderer.invoke('orb:request-permissions'),

  // Window control methods
  minimizeWindow: () => ipcRenderer.invoke('window:minimize'),
  closeWindow: () => ipcRenderer.invoke('window:close'),

  // Event listeners
  onOrbPositionUpdate: (callback) => ipcRenderer.on('orb:position-update', callback),
  onOrbStatusChange: (callback) => ipcRenderer.on('orb:status-change', callback)
});