const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { OrbBridge } = require('./orb-bridge');

let orbBridge;
let mainWindow;

async function createWindow() {
  orbBridge = new OrbBridge();
  try {
    await orbBridge.start();
    console.log('✓ Orb started via Electron');
  } catch (err) {
    console.error('Failed to start orb:', err);
    app.quit();
    return;
  }

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  ipcMain.handle('orb-query', async (_event, text) => {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Orb query timeout')), 30000);

      const handler = (response) => {
        if (response && response.type === 'query_result') {
          clearTimeout(timeout);
          orbBridge.removeMessageHandler(handler);
          resolve(response.data);
        }
      };

      orbBridge.onMessage(handler);
      orbBridge.sendMessage({ type: 'query', text });
    });
  });

  mainWindow.on('closed', () => {
    if (orbBridge) {
      orbBridge.stop();
    }
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'src', 'index.html'));
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (orbBridge) {
    orbBridge.stop();
  }
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});