// Background service worker

chrome.runtime.onInstalled.addListener(() => {
  console.log('SaaS Optimizer extension installed');
  
  // Initialize storage
  chrome.storage.local.set({
    receiptsCount: 0,
    lastSyncTime: null
  });
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'emailScanned') {
    // Update badge
    chrome.action.setBadgeText({ text: '+1' });
    chrome.action.setBadgeBackgroundColor({ color: '#28a745' });
    
    // Clear badge after 3 seconds
    setTimeout(() => {
      chrome.action.setBadgeText({ text: '' });
    }, 3000);
  }
  
  return true;
});

// Periodic background sync (optional)
chrome.alarms.create('syncReceipts', { periodInMinutes: 60 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'syncReceipts') {
    console.log('Background sync triggered');
    // Could trigger Gmail API sync here if implemented
  }
});
