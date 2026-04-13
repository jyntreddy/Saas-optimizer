const { app, BrowserWindow, ipcMain, Notification, systemPreferences } = require('electron');
const path = require('path');
const Store = require('electron-store');
const notifier = require('node-notifier');
const { machineIdSync } = require('node-machine-id');

// Services
const EmailReader = require('./services/emailReader');
const CameraScanner = require('./services/cameraScanner');
const CalendarSync = require('./services/calendarSync');
const AppMonitor = require('./services/appMonitor');
const BrowserMonitor = require('./services/browserMonitor');
const UsageAnalytics = require('./services/usageAnalytics');
const APIClient = require('./services/apiClient');

const store = new Store();
let mainWindow;
let appMonitor;
let browserMonitor;
let usageAnalytics;

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      enableRemoteModule: false,
      nodeIntegration: false
    },
    icon: path.join(__dirname, '../assets/icon.png')
  });

  // Load the backend URL or local HTML
  const backendUrl = store.get('backendUrl', 'http://localhost:8000');
  const frontendUrl = store.get('frontendUrl', 'http://localhost:8501');
  
  mainWindow.loadURL(frontendUrl);

  // Open DevTools in development
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// App lifecycle
app.whenReady().then(async () => {
  // Request permissions on macOS
  if (process.platform === 'darwin') {
    await requestMacPermissions();
  }

  createWindow();
  initializeServices();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Request macOS permissions
async function requestMacPermissions() {
  try {
    // Camera permission
    const cameraStatus = systemPreferences.getMediaAccessStatus('camera');
    if (cameraStatus !== 'granted') {
      await systemPreferences.askForMediaAccess('camera');
    }

    // Microphone permission (if needed)
    const micStatus = systemPreferences.getMediaAccessStatus('microphone');
    if (micStatus !== 'granted') {
      await systemPreferences.askForMediaAccess('microphone');
    }

    // Calendar and contacts
    console.log('✅ Permissions requested');
  } catch (error) {
    console.error('Permission request error:', error);
  }
}

// Initialize device services
function initializeServices() {
  console.log('🚀 Initializing device services...');

  const apiClient = new APIClient(
    store.get('backendUrl', 'http://localhost:8000'),
    store.get('authToken')
  );

  // Email reader service
  const emailReader = new EmailReader(apiClient);
  emailReader.startMonitoring();

  // Camera scanner service
  const cameraScanner = new CameraScanner(apiClient);

  // Calendar sync service
  const calendarSync = new CalendarSync(apiClient);
  calendarSync.startMonitoring();

  // Application usage monitor
  appMonitor = new AppMonitor();
  if (store.get('enableAppMonitoring', true)) {
    appMonitor.startMonitoring(5000); // Check every 5 seconds
    console.log('✅ Application monitoring started');
  }

  // Browser activity monitor
  browserMonitor = new BrowserMonitor();
  
  // Usage analytics aggregator
  usageAnalytics = new UsageAnalytics();
  usageAnalytics.setMonitors(appMonitor, browserMonitor);

  console.log('✅ All services initialized');
}

// IPC Handlers

// Email scanning
ipcMain.handle('scan-emails', async (event, options) => {
  try {
    const emailReader = new EmailReader(
      new APIClient(store.get('backendUrl'), store.get('authToken'))
    );
    const results = await emailReader.scanForReceipts(options);
    return { success: true, data: results };
  } catch (error) {
    console.error('Email scan error:', error);
    return { success: false, error: error.message };
  }
});

// Camera/document scanning
ipcMain.handle('scan-document', async (event, options) => {
  try {
    const cameraScanner = new CameraScanner(
      new APIClient(store.get('backendUrl'), store.get('authToken'))
    );
    const result = await cameraScanner.captureAndExtract(options);
    return { success: true, data: result };
  } catch (error) {
    console.error('Document scan error:', error);
    return { success: false, error: error.message };
  }
});

// Calendar access
ipcMain.handle('get-calendar-events', async (event, options) => {
  try {
    const calendarSync = new CalendarSync(
      new APIClient(store.get('backendUrl'), store.get('authToken'))
    );
    const events = await calendarSync.getEvents(options);
    return { success: true, data: events };
  } catch (error) {
    console.error('Calendar access error:', error);
    return { success: false, error: error.message };
  }
});

// Send notification
ipcMain.handle('send-notification', async (event, options) => {
  try {
    if (Notification.isSupported()) {
      new Notification({
        title: options.title,
        body: options.body,
        icon: options.icon || path.join(__dirname, '../assets/icon.png')
      }).show();
    } else {
      notifier.notify({
        title: options.title,
        message: options.body,
        icon: options.icon || path.join(__dirname, '../assets/icon.png'),
        sound: true
      });
    }
    return { success: true };
  } catch (error) {
    console.error('Notification error:', error);
    return { success: false, error: error.message };
  }
});

// Settings management
ipcMain.handle('get-settings', async () => {
  return store.store;
});

ipcMain.handle('set-setting', async (event, key, value) => {
  store.set(key, value);
  return { success: true };
});

// Device ID for authentication
ipcMain.handle('get-device-id', async () => {
  try {
    const deviceId = machineIdSync();
    return { success: true, deviceId };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Get application usage summary
ipcMain.handle('get-app-usage', async () => {
  try {
    if (!appMonitor) {
      return { success: false, error: 'App monitor not initialized' };
    }
    const summary = appMonitor.getUsageSummary();
    const byCategory = appMonitor.getUsageByCategory();
    const byVendor = appMonitor.getUsageByVendor();
    const currentlyRunning = appMonitor.getCurrentlyRunningApps();
    
    return { 
      success: true, 
      data: {
        summary,
        byCategory,
        byVendor,
        currentlyRunning
      }
    };
  } catch (error) {
    console.error('App usage error:', error);
    return { success: false, error: error.message };
  }
});

// Get browser history/usage
ipcMain.handle('get-browser-usage', async (event, hoursBack = 24) => {
  try {
    if (!browserMonitor) {
      return { success: false, error: 'Browser monitor not initialized' };
    }
    const summary = await browserMonitor.scanBrowserHistory(hoursBack);
    const byCategory = browserMonitor.getUsageByCategory();
    const byVendor = browserMonitor.getUsageByVendor();
    
    return { 
      success: true, 
      data: {
        summary,
        byCategory,
        byVendor
      }
    };
  } catch (error) {
    console.error('Browser usage error:', error);
    return { success: false, error: error.message };
  }
});

// Get comprehensive dashboard analytics
ipcMain.handle('get-dashboard-analytics', async () => {
  try {
    if (!usageAnalytics) {
      return { success: false, error: 'Usage analytics not initialized' };
    }
    
    // Scan browser history first
    if (browserMonitor && store.get('enableBrowserMonitoring', true)) {
      await browserMonitor.scanBrowserHistory(24 * 7); // Last 7 days
    }
    
    const dashboard = await usageAnalytics.generateDashboard();
    return { success: true, data: dashboard };
  } catch (error) {
    console.error('Dashboard analytics error:', error);
    return { success: false, error: error.message };
  }
});

// Get alternatives for subscriptions
ipcMain.handle('get-alternatives', async (event, subscriptions) => {
  try {
    if (!usageAnalytics) {
      return { success: false, error: 'Usage analytics not initialized' };
    }
    const alternatives = usageAnalytics.generateAlternatives(subscriptions);
    return { success: true, data: alternatives };
  } catch (error) {
    console.error('Alternatives error:', error);
    return { success: false, error: error.message };
  }
});

// Toggle app monitoring
ipcMain.handle('toggle-app-monitoring', async (event, enabled) => {
  try {
    store.set('enableAppMonitoring', enabled);
    
    if (enabled && !appMonitor.monitorInterval) {
      appMonitor.startMonitoring(5000);
    } else if (!enabled && appMonitor.monitorInterval) {
      appMonitor.stopMonitoring();
    }
    
    return { success: true, enabled };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Sync all usage data to backend
ipcMain.handle('sync-usage-data', async () => {
  try {
    const apiClient = new APIClient(
      store.get('backendUrl', 'http://localhost:8000'),
      store.get('authToken')
    );
    
    // Get all usage data
    const appUsage = appMonitor ? appMonitor.getUsageSummary() : [];
    const browserUsage = browserMonitor ? browserMonitor.getUsageSummary() : [];
    const dashboard = usageAnalytics ? await usageAnalytics.generateDashboard() : null;
    
    // Send to backend
    const response = await apiClient.post('/api/v1/usage/sync', {
      appUsage,
      browserUsage,
      dashboard,
      timestamp: new Date().toISOString(),
      deviceId: machineIdSync()
    });
    
    return { success: true, data: response };
  } catch (error) {
    console.error('Usage sync error:', error);
    return { success: false, error: error.message };
  }
});

// Periodic background tasks
setInterval(() => {
  // Auto-sync emails every 30 minutes
  if (store.get('autoSyncEmails', true)) {
    mainWindow?.webContents.send('trigger-email-sync');
  }

  // Check for renewal reminders
  if (store.get('enableReminders', true)) {
    mainWindow?.webContents.send('check-reminders');
  }

  // Sync usage data every hour
  if (store.get('autoSyncUsage', true)) {
    mainWindow?.webContents.send('trigger-usage-sync');
  }
}, 30 * 60 * 1000); // 30 minutes
