const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Email operations
  scanEmails: (options) => ipcRenderer.invoke('scan-emails', options),
  
  // Camera/document scanning
  scanDocument: (options) => ipcRenderer.invoke('scan-document', options),
  
  // Calendar operations
  getCalendarEvents: (options) => ipcRenderer.invoke('get-calendar-events', options),
  
  // Notifications
  sendNotification: (options) => ipcRenderer.invoke('send-notification', options),
  
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),
  
  // Device info
  getDeviceId: () => ipcRenderer.invoke('get-device-id'),
  
  // Application usage monitoring
  getAppUsage: () => ipcRenderer.invoke('get-app-usage'),
  getBrowserUsage: (hoursBack) => ipcRenderer.invoke('get-browser-usage', hoursBack),
  getDashboardAnalytics: () => ipcRenderer.invoke('get-dashboard-analytics'),
  getAlternatives: (subscriptions) => ipcRenderer.invoke('get-alternatives', subscriptions),
  toggleAppMonitoring: (enabled) => ipcRenderer.invoke('toggle-app-monitoring', enabled),
  syncUsageData: () => ipcRenderer.invoke('sync-usage-data'),
  
  // Event listeners
  onEmailSync: (callback) => ipcRenderer.on('trigger-email-sync', callback),
  onCheckReminders: (callback) => ipcRenderer.on('check-reminders', callback),
  onUsageSync: (callback) => ipcRenderer.on('trigger-usage-sync', callback),
  
  // Remove listeners
  removeEmailSyncListener: () => ipcRenderer.removeAllListeners('trigger-email-sync'),
  removeRemindersListener: () => ipcRenderer.removeAllListeners('check-reminders'),
  removeUsageSyncListener: () => ipcRenderer.removeAllListeners('trigger-usage-sync')
});

// Platform information
contextBridge.exposeInMainWorld('platform', {
  os: process.platform,
  arch: process.arch,
  version: process.version,
  isWindows: process.platform === 'win32',
  isMac: process.platform === 'darwin',
  isLinux: process.platform === 'linux'
});
