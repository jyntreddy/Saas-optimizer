/**
 * Popup UI Controller for SaaS Optimizer Gmail Scanner
 */

let backendToken = null;
let backendUrl = 'http://localhost:8000';
let isScanning = false;

// Initialize on load
document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
  await checkGmailAuth();
  await checkBackendAuth();
  setupEventListeners();
  updateUI();
});

/**
 * Load saved settings from storage
 */
async function loadSettings() {
  const storage = await chrome.storage.local.get([
    'backendToken',
    'backendUrl',
    'backendEmail',
    'receiptsCount',
    'lastScanTime',
    'autoScanEnabled'
  ]);
  
  if (storage.backendToken) {
    backendToken = storage.backendToken;
  }
  
  if (storage.backendUrl) {
    backendUrl = storage.backendUrl;
    document.getElementById('backend-url').value = backendUrl;
  }
  
  if (storage.backendEmail) {
    document.getElementById('backend-email').value = storage.backendEmail;
  }
  
  if (storage.receiptsCount) {
    document.getElementById('receipts-count').textContent = storage.receiptsCount;
  }
  
  if (storage.lastScanTime) {
    const lastScan = new Date(storage.lastScanTime);
    document.getElementById('last-scan').textContent = formatTimeAgo(lastScan);
  }
  
  if (storage.autoScanEnabled) {
    document.getElementById('auto-scan-checkbox').checked = true;
  }
}

/**
 * Check Gmail authentication status
 */
async function checkGmailAuth() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'GET_AUTH_STATUS' });
    
    if (response.authenticated) {
      showGmailConnected(response.email);
    } else {
      showGmailDisconnected();
    }
  } catch (error) {
    console.error('Error checking Gmail auth:', error);
    showGmailDisconnected();
  }
}

/**
 * Check backend authentication status
 */
async function checkBackendAuth() {
  if (backendToken) {
    showBackendConnected();
  } else {
    showBackendDisconnected();
  }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Gmail auth button
  document.getElementById('gmail-auth-btn').addEventListener('click', async () => {
    try {
      showMessage('Connecting to Gmail...', 'loading');
      const result = await chrome.runtime.sendMessage({ type: 'SCAN_GMAIL' });
      
      if (result.success) {
        await checkGmailAuth();
        showMessage('Gmail connected successfully!', 'success');
      } else {
        showMessage('Failed to connect: ' + result.error, 'error');
      }
    } catch (error) {
      showMessage('Error: ' + error.message, 'error');
    }
  });
  
  // Gmail logout button
  document.getElementById('gmail-logout-btn').addEventListener('click', async () => {
    try {
      await chrome.runtime.sendMessage({ type: 'LOGOUT' });
      showGmailDisconnected();
      showMessage('Disconnected from Gmail', 'success');
    } catch (error) {
      showMessage('Error: ' + error.message, 'error');
    }
  });
  
  // Scan button
  document.getElementById('scan-btn').addEventListener('click', startScan);
  
  // Backend login button
  document.getElementById('backend-login-btn').addEventListener('click', loginToBackend);
  
  // Backend logout button
  document.getElementById('backend-logout-btn').addEventListener('click', logoutFromBackend);
  
  // Auto-scan checkbox
  document.getElementById('auto-scan-checkbox').addEventListener('change', (e) => {
    chrome.storage.local.set({ autoScanEnabled: e.target.checked });
  });
}

/**
 * Start Gmail scan
 */
async function startScan() {
  if (isScanning) return;
  
  isScanning = true;
  document.getElementById('scan-btn').disabled = true;
  document.getElementById('progress-section').classList.remove('hidden');
  document.getElementById('progress-fill').style.width = '0%';
  document.getElementById('progress-text').textContent = 'Starting scan...';
  
  try {
    const result = await chrome.runtime.sendMessage({ type: 'SCAN_GMAIL' });
    
    if (result.success) {
      document.getElementById('receipts-count').textContent = result.receipts;
      document.getElementById('last-scan').textContent = 'Just now';
      
      await chrome.storage.local.set({
        receiptsCount: result.receipts,
        lastScanTime: new Date().toISOString()
      });
      
      if (result.pending) {
        showMessage(`Found ${result.receipts} receipts! Login to backend to sync.`, 'success');
      } else {
        showMessage(`Successfully scanned ${result.receipts} receipts!`, 'success');
      }
    } else {
      showMessage('Scan failed: ' + result.error, 'error');
    }
  } catch (error) {
    showMessage('Error: ' + error.message, 'error');
  } finally {
    isScanning = false;
    document.getElementById('scan-btn').disabled = false;
    document.getElementById('progress-section').classList.add('hidden');
  }
}

/**
 * Login to backend
 */
async function loginToBackend() {
  const email = document.getElementById('backend-email').value;
  const password = document.getElementById('backend-password').value;
  backendUrl = document.getElementById('backend-url').value;
  
  if (!email || !password) {
    showBackendMessage('Please enter email and password', 'error');
    return;
  }
  
  try {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${backendUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    backendToken = data.access_token;
    
    // Save to storage
    await chrome.storage.local.set({
      backendToken,
      backendUrl,
      backendEmail: email
    });
    
    // Send token to background script
    await chrome.runtime.sendMessage({
      type: 'SET_BACKEND_TOKEN',
      token: backendToken
    });
    
    showBackendConnected();
    showMessage('Backend connected successfully!', 'success');
    
    // Check for pending receipts
    const storage = await chrome.storage.local.get(['pendingReceipts']);
    if (storage.pendingReceipts && storage.pendingReceipts.length > 0) {
      showMessage(`Syncing ${storage.pendingReceipts.length} pending receipts...`, 'loading');
      // Trigger a scan to upload pending receipts
      setTimeout(() => startScan(), 1000);
    }
    
  } catch (error) {
    showBackendMessage('Login failed: ' + error.message, 'error');
  }
}

/**
 * Logout from backend
 */
async function logoutFromBackend() {
  await chrome.storage.local.remove(['backendToken', 'backendEmail']);
  backendToken = null;
  
  await chrome.runtime.sendMessage({
    type: 'SET_BACKEND_TOKEN',
    token: null
  });
  
  showBackendDisconnected();
  showMessage('Disconnected from backend', 'success');
}

/**
 * Show Gmail connected state
 */
function showGmailConnected(email) {
  document.getElementById('gmail-disconnected').classList.add('hidden');
  document.getElementById('gmail-connected').classList.remove('hidden');
  document.getElementById('gmail-email').textContent = email || 'Connected';
  document.getElementById('scan-section').classList.remove('hidden');
}

/**
 * Show Gmail disconnected state
 */
function showGmailDisconnected() {
  document.getElementById('gmail-disconnected').classList.remove('hidden');
  document.getElementById('gmail-connected').classList.add('hidden');
  document.getElementById('scan-section').classList.add('hidden');
}

/**
 * Show backend connected state
 */
function showBackendConnected() {
  document.getElementById('backend-login').classList.add('hidden');
  document.getElementById('backend-connected').classList.remove('hidden');
}

/**
 * Show backend disconnected state
 */
function showBackendDisconnected() {
  document.getElementById('backend-login').classList.remove('hidden');
  document.getElementById('backend-connected').classList.add('hidden');
}

/**
 * Show message to user
 */
function showMessage(text, type) {
  const container = document.getElementById('message-container');
  container.innerHTML = `<div class="message ${type}">${text}</div>`;
  
  if (type !== 'loading') {
    setTimeout(() => {
      container.innerHTML = '';
    }, 5000);
  }
}

/**
 * Show backend-specific message
 */
function showBackendMessage(text, type) {
  const container = document.getElementById('backend-message');
  container.innerHTML = `<div class="message ${type}">${text}</div>`;
  
  setTimeout(() => {
    container.innerHTML = '';
  }, 5000);
}

/**
 * Update UI
 */
function updateUI() {
  // Any periodic updates can go here
}

/**
 * Format time ago
 */
function formatTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  
  if (seconds < 60) return 'Just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

/**
 * Listen for scan progress updates
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'SCAN_PROGRESS') {
    document.getElementById('progress-fill').style.width = request.progress + '%';
    document.getElementById('progress-text').textContent = 
      `Scanned ${request.receipts} receipts (${request.progress}%)`;
  }
});

console.log('Popup script loaded');
  });
});

// Auto-scan receipts
document.getElementById('auto-scan-btn').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (!tab.url.includes('mail.google.com')) {
    showMessage('scan-message', 'Please open Gmail inbox first', 'error');
    return;
  }
  
  showMessage('scan-message', 'Auto-scanning emails...', 'success');
  
  // Send message to content script
  chrome.tabs.sendMessage(tab.id, { action: 'autoScanReceipts' }, (response) => {
    if (response && response.success) {
      showMessage('scan-message', `Found ${response.count} potential receipts`, 'success');
      // Process each email
      response.emails.forEach(email => sendEmailToAPI(email));
    }
  });
});

// Send email data to API
async function sendEmailToAPI(emailData) {
  if (!accessToken) {
    showMessage('scan-message', 'Please login first', 'error');
    return;
  }
  
  try {
    const response = await fetch(`${apiUrl}/api/v1/emails/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({
        email_subject: emailData.subject,
        sender_email: emailData.from,
        raw_body: emailData.body,
        received_date: emailData.date || new Date().toISOString()
      })
    });
    
    if (!response.ok) {
      throw new Error('API request failed');
    }
    
    const data = await response.json();
    
    // Update counters
    sessionCount++;
    document.getElementById('session-count').textContent = sessionCount;
    
    chrome.storage.local.get(['receiptsCount'], (result) => {
      const totalCount = (result.receiptsCount || 0) + 1;
      chrome.storage.local.set({ receiptsCount: totalCount });
      document.getElementById('receipts-count').textContent = totalCount;
    });
    
    if (data.is_subscription && data.confidence_score > 0.5) {
      showMessage('scan-message', 
        `✅ Found: ${data.vendor || 'Unknown'} - $${data.amount || '?'}`, 
        'success');
    } else {
      showMessage('scan-message', '✓ Email scanned (low confidence)', 'success');
    }
    
  } catch (error) {
    showMessage('scan-message', 'Error: ' + error.message, 'error');
  }
}

// UI helpers
function showMainSection() {
  document.getElementById('login-section').classList.add('hidden');
  document.getElementById('main-section').classList.remove('hidden');
  updateStatus();
}

function showLoginSection() {
  document.getElementById('login-section').classList.remove('hidden');
  document.getElementById('main-section').classList.add('hidden');
}

function updateStatus() {
  const statusEl = document.getElementById('status');
  const statusText = document.getElementById('status-text');
  
  if (accessToken) {
    statusEl.className = 'status connected';
    statusText.textContent = '✓ Connected to SaaS Optimizer';
  } else {
    statusEl.className = 'status disconnected';
    statusText.textContent = '✗ Not connected';
  }
}

function showMessage(elementId, message, type) {
  const messageEl = document.getElementById(elementId);
  messageEl.className = `message ${type}`;
  messageEl.textContent = message;
  messageEl.style.display = 'block';
  
  setTimeout(() => {
    messageEl.style.display = 'none';
  }, 5000);
}
