/**
 * SaaS Optimizer Chrome Extension - Background Service Worker
 * Handles Gmail API authentication and email scanning
 */

const BACKEND_URL = 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

// Gmail API configuration
const GMAIL_API_BASE = 'https://gmail.googleapis.com/gmail/v1';

// Known SaaS vendors to detect in emails
const SAAS_VENDORS = [
  'netflix', 'spotify', 'adobe', 'microsoft', 'google', 'amazon',
  'slack', 'zoom', 'notion', 'figma', 'github', 'heroku',
  'aws', 'digitalocean', 'dropbox', 'salesforce', 'hubspot',
  'mailchimp', 'sendgrid', 'twilio', 'stripe', 'shopify',
  'asana', 'trello', 'monday', 'clickup', 'airtable'
];

// Authentication state
let accessToken = null;
let userEmail = null;

/**
 * Get OAuth2 access token using Chrome Identity API
 */
async function getAuthToken() {
  return new Promise((resolve, reject) => {
    chrome.identity.getAuthToken({ interactive: true }, (token) => {
      if (chrome.runtime.lastError) {
        reject(chrome.runtime.lastError);
        return;
      }
      accessToken = token;
      resolve(token);
    });
  });
}

/**
 * Remove cached OAuth token
 */
async function removeAuthToken() {
  if (accessToken) {
    return new Promise((resolve) => {
      chrome.identity.removeCachedAuthToken({ token: accessToken }, () => {
        accessToken = null;
        userEmail = null;
        resolve();
      });
    });
  }
}

/**
 * Get user's email address
 */
async function getUserEmail(token) {
  const response = await fetch('https://www.googleapis.com/oauth2/v1/userinfo?alt=json', {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Failed to get user info');
  }
  
  const data = await response.json();
  userEmail = data.email;
  return data.email;
}

/**
 * Search Gmail for subscription receipts
 */
async function searchGmailReceipts(token, query = '', maxResults = 100) {
  // Build search query for subscription-related emails
  const searchQuery = query || [
    'subject:(receipt OR invoice OR subscription OR payment OR billing)',
    'from:(' + SAAS_VENDORS.join(' OR ') + ')',
    'newer_than:1y'
  ].join(' ');
  
  const url = `${GMAIL_API_BASE}/users/me/messages?q=${encodeURIComponent(searchQuery)}&maxResults=${maxResults}`;
  
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error(`Gmail API error: ${response.status}`);
  }
  
  const data = await response.json();
  return data.messages || [];
}

/**
 * Get full message details
 */
async function getMessageDetails(token, messageId) {
  const url = `${GMAIL_API_BASE}/users/me/messages/${messageId}?format=full`;
  
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to get message: ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Parse email headers
 */
function getHeader(headers, name) {
  const header = headers.find(h => h.name.toLowerCase() === name.toLowerCase());
  return header ? header.value : null;
}

/**
 * Decode base64url encoded data
 */
function decodeBase64Url(str) {
  try {
    // Replace URL-safe characters
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    // Pad with = to make length multiple of 4
    while (str.length % 4) {
      str += '=';
    }
    return atob(str);
  } catch (e) {
    console.error('Base64 decode error:', e);
    return '';
  }
}

/**
 * Extract receipt data from email
 */
function parseReceiptData(message) {
  const headers = message.payload.headers;
  const subject = getHeader(headers, 'subject') || '';
  const from = getHeader(headers, 'from') || '';
  const date = getHeader(headers, 'date') || '';
  
  // Get email body
  let body = '';
  if (message.payload.body && message.payload.body.data) {
    body = decodeBase64Url(message.payload.body.data);
  } else if (message.payload.parts) {
    // Multi-part message
    for (const part of message.payload.parts) {
      if (part.mimeType === 'text/plain' || part.mimeType === 'text/html') {
        if (part.body && part.body.data) {
          body += decodeBase64Url(part.body.data);
        }
      }
    }
  }
  
  // Extract vendor
  let vendor = '';
  for (const v of SAAS_VENDORS) {
    if (from.toLowerCase().includes(v) || subject.toLowerCase().includes(v)) {
      vendor = v.charAt(0).toUpperCase() + v.slice(1);
      break;
    }
  }
  
  // Extract amount (look for currency patterns)
  const amountRegex = /\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)|(\d+(?:,\d{3})*(?:\.\d{2})?)\s*USD/gi;
  const amountMatches = body.match(amountRegex);
  let amount = null;
  
  if (amountMatches && amountMatches.length > 0) {
    const amountStr = amountMatches[0].replace(/[\$,USD\s]/g, '');
    amount = parseFloat(amountStr);
  }
  
  return {
    messageId: message.id,
    subject,
    from,
    date: new Date(date).toISOString(),
    vendor: vendor || extractDomain(from),
    amount,
    snippet: message.snippet,
    body: body.substring(0, 500) // First 500 chars
  };
}

/**
 * Extract domain from email address
 */
function extractDomain(email) {
  const match = email.match(/@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
  if (match) {
    const domain = match[1].split('.')[0];
    return domain.charAt(0).toUpperCase() + domain.slice(1);
  }
  return 'Unknown';
}

/**
 * Send receipts to backend
 */
async function sendReceiptsToBackend(receipts, authToken) {
  const response = await fetch(`${BACKEND_URL}${API_V1_PREFIX}/emails/upload`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      source: 'gmail_extension',
      receipts: receipts,
      scanned_at: new Date().toISOString()
    })
  });
  
  if (!response.ok) {
    throw new Error(`Backend upload failed: ${response.status}`);
  }
  
  return await response.json();
}

/**
 * Main scan function
 */
async function scanGmailForReceipts() {
  try {
    // Get auth token
    const token = await getAuthToken();
    
    if (!userEmail) {
      await getUserEmail(token);
    }
    
    // Search for receipts
    console.log('Searching Gmail for receipts...');
    const messages = await searchGmailReceipts(token);
    
    console.log(`Found ${messages.length} potential receipt emails`);
    
    // Get details for each message
    const receipts = [];
    let processed = 0;
    
    for (const msg of messages.slice(0, 50)) { // Limit to 50 for now
      try {
        const details = await getMessageDetails(token, msg.id);
        const receipt = parseReceiptData(details);
        
        if (receipt.amount) { // Only include if we found an amount
          receipts.push(receipt);
        }
        
        processed++;
        
        // Update progress
        chrome.runtime.sendMessage({
          type: 'SCAN_PROGRESS',
          progress: Math.round((processed / messages.length) * 100),
          receipts: receipts.length
        });
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`Error processing message ${msg.id}:`, error);
      }
    }
    
    console.log(`Extracted ${receipts.length} receipts with amounts`);
    
    // Get backend auth token from storage
    const storage = await chrome.storage.local.get(['backendToken']);
    
    if (storage.backendToken) {
      // Send to backend
      console.log('Sending receipts to backend...');
      const result = await sendReceiptsToBackend(receipts, storage.backendToken);
      
      console.log('Upload complete:', result);
      
      // Show notification
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.svg',
        title: 'Gmail Scan Complete',
        message: `Found ${receipts.length} subscription receipts!`
      });
      
      // Update badge
      chrome.action.setBadgeText({ text: String(receipts.length) });
      chrome.action.setBadgeBackgroundColor({ color: '#28a745' });
      
      return { success: true, receipts: receipts.length, result };
    } else {
      // Store receipts locally
      await chrome.storage.local.set({ pendingReceipts: receipts });
      
      return { success: true, receipts: receipts.length, pending: true };
    }
    
  } catch (error) {
    console.error('Gmail scan error:', error);
    
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.svg',
      title: 'Scan Failed',
      message: error.message
    });
    
    throw error;
  }
}

/**
 * Message listener
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'SCAN_GMAIL') {
    scanGmailForReceipts()
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Will respond asynchronously
  }
  
  if (request.type === 'GET_AUTH_STATUS') {
    sendResponse({
      authenticated: !!accessToken,
      email: userEmail
    });
    return true;
  }
  
  if (request.type === 'LOGOUT') {
    removeAuthToken()
      .then(() => sendResponse({ success: true }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  
  if (request.type === 'SET_BACKEND_TOKEN') {
    chrome.storage.local.set({ backendToken: request.token }, () => {
      sendResponse({ success: true });
    });
    return true;
  }
});

/**
 * Install listener
 */
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('SaaS Optimizer extension installed!');
    
    // Open popup
    chrome.action.openPopup();
  }
});

/**
 * Periodic background sync
 */
chrome.alarms.create('autoScan', { periodInMinutes: 60 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'autoScan') {
    const storage = await chrome.storage.local.get(['autoScanEnabled', 'backendToken']);
    
    if (storage.autoScanEnabled && storage.backendToken) {
      console.log('Running automatic Gmail scan...');
      try {
        await scanGmailForReceipts();
      } catch (error) {
        console.error('Auto-scan failed:', error);
      }
    }
  }
});

console.log('SaaS Optimizer Gmail Scanner background script loaded');
