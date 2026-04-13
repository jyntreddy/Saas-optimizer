// Content script for Gmail - extracts email data

console.log('SaaS Optimizer: Content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'scanCurrentEmail') {
    const emailData = extractCurrentEmail();
    sendResponse({ success: !!emailData, data: emailData });
  } else if (request.action === 'autoScanReceipts') {
    const emails = scanInboxForReceipts();
    sendResponse({ success: true, count: emails.length, emails: emails });
  }
  return true; // Keep channel open for async response
});

// Extract data from currently open email
function extractCurrentEmail() {
  try {
    // Gmail's email view structure
    const subjectEl = document.querySelector('h2.hP');
    const fromEl = document.querySelector('span.gD');
    const dateEl = document.querySelector('span.g3');
    const bodyEl = document.querySelector('div.a3s.aiL');
    
    if (!subjectEl || !fromEl || !bodyEl) {
      return null;
    }
    
    return {
      subject: subjectEl.textContent.trim(),
      from: extractEmail(fromEl.getAttribute('email') || fromEl.textContent),
      date: dateEl ? parseDateString(dateEl.getAttribute('title')) : new Date().toISOString(),
      body: bodyEl.innerText
    };
  } catch (error) {
    console.error('Error extracting email:', error);
    return null;
  }
}

// Scan inbox for receipt-like emails
function scanInboxForReceipts() {
  const emails = [];
  
  try {
    // Find all email rows in inbox
    const emailRows = document.querySelectorAll('tr.zA');
    
    const receiptKeywords = [
      'receipt', 'invoice', 'payment', 'subscription',
      'billing', 'charged', 'renewal', 'order confirmation'
    ];
    
    emailRows.forEach((row, index) => {
      if (index >= 20) return; // Limit to 20 emails
      
      const subjectEl = row.querySelector('span.bog');
      const fromEl = row.querySelector('span.yX.xY');
      
      if (!subjectEl) return;
      
      const subject = subjectEl.textContent.toLowerCase();
      
      // Check if subject contains receipt keywords
      const isReceipt = receiptKeywords.some(keyword => 
        subject.includes(keyword)
      );
      
      if (isReceipt && fromEl) {
        // Note: We can only get limited data from inbox view
        // User would need to click through for full email
        emails.push({
          subject: subjectEl.textContent.trim(),
          from: fromEl.textContent.trim(),
          date: new Date().toISOString(),
          body: 'Auto-scanned from inbox (limited data)',
          preview: true
        });
      }
    });
  } catch (error) {
    console.error('Error scanning inbox:', error);
  }
  
  return emails;
}

// Add visual indicator to receipt emails
function highlightReceiptEmails() {
  const emailRows = document.querySelectorAll('tr.zA');
  
  const receiptKeywords = [
    'receipt', 'invoice', 'payment', 'subscription',
    'billing', 'charged', 'renewal'
  ];
  
  emailRows.forEach(row => {
    const subjectEl = row.querySelector('span.bog');
    if (!subjectEl) return;
    
    const subject = subjectEl.textContent.toLowerCase();
    const isReceipt = receiptKeywords.some(k => subject.includes(k));
    
    if (isReceipt && !row.classList.contains('saas-optimizer-receipt')) {
      row.classList.add('saas-optimizer-receipt');
      row.style.borderLeft = '3px solid #28a745';
      
      // Add badge
      const badge = document.createElement('span');
      badge.textContent = '💰';
      badge.className = 'saas-optimizer-badge';
      badge.style.marginLeft = '5px';
      badge.title = 'Potential receipt detected';
      subjectEl.appendChild(badge);
    }
  });
}

// Helper functions
function extractEmail(text) {
  const match = text.match(/[\w\.-]+@[\w\.-]+\.\w+/);
  return match ? match[0] : text;
}

function parseDateString(dateStr) {
  try {
    return new Date(dateStr).toISOString();
  } catch {
    return new Date().toISOString();
  }
}

// Observe inbox changes and highlight receipts
const observer = new MutationObserver(() => {
  highlightReceiptEmails();
});

// Start observing when inbox loads
setTimeout(() => {
  const inbox = document.querySelector('div.AO');
  if (inbox) {
    observer.observe(inbox, { childList: true, subtree: true });
    highlightReceiptEmails();
  }
}, 2000);
