// Popup script for SaaS Optimizer extension

let apiUrl = 'http://localhost:8000';
let accessToken = null;
let sessionCount = 0;

// Load saved settings
chrome.storage.local.get(['apiUrl', 'accessToken', 'receiptsCount'], (result) => {
  if (result.apiUrl) {
    apiUrl = result.apiUrl;
    document.getElementById('api-url').value = apiUrl;
  }
  
  if (result.accessToken) {
    accessToken = result.accessToken;
    showMainSection();
  }
  
  if (result.receiptsCount) {
    document.getElementById('receipts-count').textContent = result.receiptsCount;
  }
});

// Login
document.getElementById('login-btn').addEventListener('click', async () => {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  apiUrl = document.getElementById('api-url').value;
  
  if (!email || !password) {
    showMessage('login-message', 'Please enter email and password', 'error');
    return;
  }
  
  try {
    // Login to API
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
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
    accessToken = data.access_token;
    
    // Save credentials
    chrome.storage.local.set({ 
      apiUrl: apiUrl,
      accessToken: accessToken,
      userEmail: email
    });
    
    showMessage('login-message', 'Login successful!', 'success');
    setTimeout(() => {
      showMainSection();
    }, 1000);
    
  } catch (error) {
    showMessage('login-message', 'Login failed: ' + error.message, 'error');
  }
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
  chrome.storage.local.remove(['accessToken', 'userEmail']);
  accessToken = null;
  showLoginSection();
});

// Scan current email
document.getElementById('scan-btn').addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (!tab.url.includes('mail.google.com')) {
    showMessage('scan-message', 'Please open a Gmail email first', 'error');
    return;
  }
  
  // Send message to content script
  chrome.tabs.sendMessage(tab.id, { action: 'scanCurrentEmail' }, (response) => {
    if (chrome.runtime.lastError) {
      showMessage('scan-message', 'Error: ' + chrome.runtime.lastError.message, 'error');
      return;
    }
    
    if (response && response.success) {
      sendEmailToAPI(response.data);
    } else {
      showMessage('scan-message', 'Could not extract email data', 'error');
    }
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
