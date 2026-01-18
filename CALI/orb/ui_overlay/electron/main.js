// UCM_4_Core/CALI/orb/ui_overlay/electron/main.js
const { app, BrowserWindow, ipcMain, dialog, screen } = require('electron');
const path = require('path');
const WebSocket = require('ws');

// Global references
let mainWindow;
let pythonWs = null;
let reconnectInterval;

// Window configuration
const WINDOW_CONFIG = {
    width: 120,
    height: 120,
    frame: false,
    transparent: true, // Restore transparency for proper desktop overlay
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    show: true,
    backgroundColor: '#00000000', // Transparent background
    webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
    }
};

function createWindow() {
    console.log('[ELECTRON] Creating ORB window...');

    // Create the browser window
    mainWindow = new BrowserWindow(WINDOW_CONFIG);

    console.log('[ELECTRON] Window created, loading HTML...');

    // Load the app
    mainWindow.loadFile('index.html');

    console.log('[ELECTRON] HTML loaded, positioning window...');

    // Position in center initially, then let Python control positioning
    const { width, height } = screen.getPrimaryDisplay().size;
    mainWindow.setPosition(width/2 - 60, height/2 - 60); // Center the 120x120 window

    console.log('[ELECTRON] Window positioned, setting always on top...');

    // Ensure it's always on top
    mainWindow.setAlwaysOnTop(true, 'screen-saver');

    console.log('[ELECTRON] ORB window ready!');

    // Handle window closed
    mainWindow.on('closed', () => {
        console.log('[ELECTRON] ORB window closed');
        mainWindow = null;
    });

    // Connect to Python WebSocket
    connectToPython();
}

function connectToPython() {
    console.log('[ELECTRON] Connecting to Python ORB...');

    pythonWs = new WebSocket('ws://localhost:8766'); // Python UI commands port

    pythonWs.on('open', () => {
        console.log('[ELECTRON] Connected to Python ORB');
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    });

    pythonWs.on('message', (data) => {
        try {
            const command = JSON.parse(data.toString());
            handlePythonCommand(command);
        } catch (e) {
            console.error('[ELECTRON] Invalid command:', e);
        }
    });

    pythonWs.on('close', () => {
        console.log('[ELECTRON] Disconnected from Python ORB');
        // Auto-reconnect
        if (!reconnectInterval) {
            reconnectInterval = setInterval(connectToPython, 5000);
        }
    });

    pythonWs.on('error', (error) => {
        console.error('[ELECTRON] WebSocket error:', error);
    });
}

function handlePythonCommand(command) {
    if (!mainWindow || mainWindow.isDestroyed()) return;

    switch (command.command) {
        case 'show':
            mainWindow.show();
            mainWindow.setAlwaysOnTop(true, 'screen-saver');
            break;

        case 'hide':
            mainWindow.hide();
            break;

        case 'update_position':
            updateWindowPosition(command);
            break;

        case 'show_resolution':
            showResolutionInterface(command);
            break;

        case 'update_state':
            updateOrbState(command);
            break;

        case 'update_status':
            updateStatus(command);
            break;

        default:
            // Handle non-command messages (like connection_established)
            if (command.type === 'connection_established') {
                console.log('[ELECTRON] WebSocket connection established');
            } else {
                console.log('[ELECTRON] Unknown message:', command);
            }
    }
}

function updateWindowPosition(command) {
    if (!mainWindow || mainWindow.isDestroyed()) return;

    const { x, y, application } = command;

    // Smooth position updates
    const [currentX, currentY] = mainWindow.getPosition();
    const smoothX = currentX + (x - currentX) * 0.3;
    const smoothY = currentY + (y - currentY) * 0.3;

    mainWindow.setPosition(Math.round(smoothX), Math.round(smoothY));

    // Send application context to renderer
    if (application) {
        mainWindow.webContents.send('application-context', application);
    }
}

function showResolutionInterface(command) {
    if (!mainWindow || mainWindow.isDestroyed()) return;

    mainWindow.webContents.send('show-resolution', command.data);
    mainWindow.show();
    mainWindow.focus();
}

function updateOrbState(command) {
    if (!mainWindow || mainWindow.isDestroyed()) return;

    mainWindow.webContents.send('update-orb-state', command.state);
}

function updateStatus(command) {
    if (!mainWindow || mainWindow.isDestroyed()) return;

    mainWindow.webContents.send('update-status', command.status, command.theme);
}

// IPC handlers for renderer communication
ipcMain.handle('get-screen-size', () => {
    const { width, height } = screen.getPrimaryDisplay().size;
    return { width, height };
});

ipcMain.handle('request-permission', async (event, request) => {
    const result = await dialog.showMessageBox(mainWindow, {
        type: 'question',
        buttons: ['Deny', 'Allow Once', 'Allow Always'],
        defaultId: 0,
        cancelId: 0,
        title: 'ORB Browser Permission Request',
        message: `ORB wants to access your browser data`,
        detail: `"${request.application}" wants to read:\n• Your master dashboard\n• Current browser tab\n\nThis helps ORB provide better resolution guidance.`
    });

    return {
        granted: result.response > 0,
        persistent: result.response === 2,
        application: request.application
    };
});

ipcMain.handle('send-to-python', (event, message) => {
    if (pythonWs && pythonWs.readyState === WebSocket.OPEN) {
        pythonWs.send(JSON.stringify(message));
    }
});

// App event handlers
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (pythonWs) {
        pythonWs.close();
    }
    if (reconnectInterval) {
        clearInterval(reconnectInterval);
    }
    app.quit();
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Handle app being closed
process.on('exit', () => {
    if (pythonWs) {
        pythonWs.close();
    }
});