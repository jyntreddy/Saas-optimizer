const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // Email operations
  scanEmails: (options) => ipcRenderer.invoke('scan-emails', options),
  
  // SMS operations
  scanSMS: (options) => ipcRenderer.invoke('scan-sms', options),
  
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
  
  // Event listeners
  onEmailSync: (callback) => ipcRenderer.on('trigger-email-sync', callback),
  onSMSSync: (callback) => ipcRenderer.on('trigger-sms-sync', callback),
  onCheckReminders: (callback) => ipcRenderer.on('check-reminders', callback),
  
  // Remove listeners
  removeEmailSyncListener: () => ipcRenderer.removeAllListeners('trigger-email-sync'),
  removeSMSSyncListener: () => ipcRenderer.removeAllListeners('trigger-sms-sync'),
  removeRemindersListener: () => ipcRenderer.removeAllListeners('check-reminders')
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
