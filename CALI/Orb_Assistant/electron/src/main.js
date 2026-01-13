const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const { CALILauncher } = require('./cali-launcher');

class CALIElectronApp {
  constructor() {
    this.launcher = null;
    this.mainWindow = null;
    this.logQueue = [];
    this.isQuitting = false;
    this.repoRoot = path.join(__dirname, '..'); // electron folder
  }

  async initialize() {
    try {
      this.launcher = new CALILauncher(this.repoRoot);
      this.setupLauncherHandlers();
      await this.launcher.startAll();
      await this.createWindow();
      this.setupIpcHandlers();
      this.buildApplicationMenu();
      console.log('✓ CALI UCM_4_Core Electron initialized (stub mode)');
    } catch (error) {
      console.error('Initialization failed:', error);
      this.showErrorDialog('CALI Startup Error', error.message || String(error));
      app.exit(1);
    }
  }

  setupLauncherHandlers() {
    this.launcher.on('log', (log) => {
      const entry = { timestamp: Date.now(), level: 'info', ...log };
      this.logQueue.push(entry);
      if (this.logQueue.length > 1000) this.logQueue.shift();
      if (this.mainWindow) {
        this.mainWindow.webContents.send('cali-log', entry);
      }
    });

    this.launcher.on('core-status', ({ core, status }) => {
      if (this.mainWindow) {
        this.mainWindow.webContents.send('core-status', { core, status });
      }
    });
  }

  async createWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1600,
      height: 1000,
      minWidth: 1200,
      minHeight: 700,
      title: 'CALI UCM_4_Core v2.1',
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js'),
      },
      show: false,
      icon: path.join(__dirname, 'assets', 'cali-icon.png'),
    });

    const uiPath = path.join(__dirname, 'ui', 'index.html');
    await this.mainWindow.loadFile(uiPath);

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow.show();
      this.mainWindow.webContents.send('system-status', this.launcher.getSystemStatus());
    });

    this.mainWindow.on('close', async (event) => {
      if (!this.isQuitting) {
        event.preventDefault();
        await this.shutdown();
      }
    });
  }

  setupIpcHandlers() {
    ipcMain.handle('cali-query', async (_event, text) => {
      const caliProcess = this.launcher.processes.get('cali');
      if (!caliProcess) {
        throw new Error('CALI orchestrator stub not running');
      }
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('Query timeout')), 30000);
        const handler = (data) => {
          const line = data.toString();
          if (line.startsWith('{')) {
            try {
              const parsed = JSON.parse(line);
              if (parsed.type === 'result') {
                clearTimeout(timeout);
                caliProcess.stdout.off('data', handler);
                resolve(parsed.data);
              }
            } catch (err) {
              // ignore
            }
          }
        };
        caliProcess.stdout.on('data', handler);
        caliProcess.stdin.write(JSON.stringify({ type: 'query', text }) + '\n');
      });
    });

    ipcMain.handle('cali-stop-core', (_event, coreName) => {
      this.launcher.stopCore(coreName);
    });

    ipcMain.handle('cali-restart-core', async (_event, coreName) => {
      await this.launcher.restartCore(coreName);
    });

    ipcMain.handle('cali-stop-all', () => {
      this.launcher.stopAll();
    });

    ipcMain.handle('cali-get-status', () => {
      return this.launcher.getSystemStatus();
    });

    ipcMain.handle('cali-get-logs', (_event, limit = 100) => {
      return this.logQueue.slice(-limit);
    });
  }

  buildApplicationMenu() {
    const template = [
      {
        label: 'CALI',
        submenu: [
          { role: 'about' },
          { type: 'separator' },
          { role: 'quit' },
        ],
      },
      {
        label: 'System',
        submenu: [
          {
            label: 'Emergency Stop',
            accelerator: 'CmdOrCtrl+E',
            click: () => this.shutdown(),
          },
          {
            label: 'Restart Core',
            submenu: ['kaygee', 'caleon', 'cali', 'cali_x_one', 'ucm_core_ecm'].map((core) => ({
              label: core,
              click: () => this.launcher.restartCore(core),
            })),
          },
        ],
      },
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  async shutdown() {
    if (this.isQuitting) return;
    this.isQuitting = true;
    this.mainWindow?.webContents.send('app-shutdown');
    this.launcher.stopAll();
    await new Promise((resolve) => setTimeout(resolve, 500));
    app.quit();
  }

  showErrorDialog(title, message) {
    dialog.showErrorBox(title, message);
  }
}

const caliApp = new CALIElectronApp();
app.whenReady().then(() => caliApp.initialize());

app.on('window-all-closed', () => {
  app.quit();
});

app.on('before-quit', async () => {
  await caliApp.shutdown();
});
