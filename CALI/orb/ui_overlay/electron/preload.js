// UCM_4_Core/CALI/orb/ui_overlay/electron/preload.js
const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Get screen size
    getScreenSize: () => ipcRenderer.invoke('get-screen-size'),

    // Request browser permission
    requestPermission: (request) => ipcRenderer.invoke('request-permission', request),

    // Send message to Python
    sendToPython: (message) => ipcRenderer.invoke('send-to-python', message),

    // Listen for events from main process
    onApplicationContext: (callback) => ipcRenderer.on('application-context', callback),
    onShowResolution: (callback) => ipcRenderer.on('show-resolution', callback),
    onUpdateOrbState: (callback) => ipcRenderer.on('update-orb-state', callback),
    onUpdateStatus: (callback) => ipcRenderer.on('update-status', callback),

    // Remove listeners
    removeAllListeners: (event) => ipcRenderer.removeAllListeners(event)
});