const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');

/**
 * Browser Activity Monitor Service
 * Tracks web-based SaaS usage through browser history
 * Supports Chrome, Firefox, Edge, Safari
 */
class BrowserMonitor {
  constructor() {
    this.platform = os.platform();
    this.homeDir = os.homedir();
    this.browserPaths = this.getBrowserPaths();
    
    // Known SaaS web applications and their domains
    this.saasPatterns = {
      // Communication & Collaboration
      'slack.com': { name: 'Slack', category: 'Communication', vendor: 'Slack' },
      'teams.microsoft.com': { name: 'Microsoft Teams', category: 'Communication', vendor: 'Microsoft' },
      'zoom.us': { name: 'Zoom', category: 'Communication', vendor: 'Zoom' },
      'discord.com': { name: 'Discord', category: 'Communication', vendor: 'Discord' },
      
      // Productivity
      'notion.so': { name: 'Notion', category: 'Productivity', vendor: 'Notion' },
      'todoist.com': { name: 'Todoist', category: 'Productivity', vendor: 'Todoist' },
      'trello.com': { name: 'Trello', category: 'Productivity', vendor: 'Atlassian' },
      'asana.com': { name: 'Asana', category: 'Productivity', vendor: 'Asana' },
      'monday.com': { name: 'Monday.com', category: 'Productivity', vendor: 'Monday.com' },
      'airtable.com': { name: 'Airtable', category: 'Productivity', vendor: 'Airtable' },
      'coda.io': { name: 'Coda', category: 'Productivity', vendor: 'Coda' },
      'evernote.com': { name: 'Evernote', category: 'Productivity', vendor: 'Evernote' },
      
      // Development
      'github.com': { name: 'GitHub', category: 'Development', vendor: 'GitHub' },
      'gitlab.com': { name: 'GitLab', category: 'Development', vendor: 'GitLab' },
      'bitbucket.org': { name: 'Bitbucket', category: 'Development', vendor: 'Atlassian' },
      'vercel.com': { name: 'Vercel', category: 'Development', vendor: 'Vercel' },
      'netlify.com': { name: 'Netlify', category: 'Development', vendor: 'Netlify' },
      'heroku.com': { name: 'Heroku', category: 'Development', vendor: 'Salesforce' },
      'aws.amazon.com': { name: 'AWS Console', category: 'Development', vendor: 'Amazon' },
      'cloud.google.com': { name: 'Google Cloud', category: 'Development', vendor: 'Google' },
      'portal.azure.com': { name: 'Azure Portal', category: 'Development', vendor: 'Microsoft' },
      
      // Design
      'figma.com': { name: 'Figma', category: 'Design', vendor: 'Figma' },
      'sketch.com': { name: 'Sketch', category: 'Design', vendor: 'Sketch' },
      'canva.com': { name: 'Canva', category: 'Design', vendor: 'Canva' },
      'invision.com': { name: 'InVision', category: 'Design', vendor: 'InVision' },
      'miro.com': { name: 'Miro', category: 'Design', vendor: 'Miro' },
      
      // Cloud Storage
      'dropbox.com': { name: 'Dropbox', category: 'Cloud Storage', vendor: 'Dropbox' },
      'drive.google.com': { name: 'Google Drive', category: 'Cloud Storage', vendor: 'Google' },
      'onedrive.live.com': { name: 'OneDrive', category: 'Cloud Storage', vendor: 'Microsoft' },
      'box.com': { name: 'Box', category: 'Cloud Storage', vendor: 'Box' },
      
      // Project Management
      'atlassian.net': { name: 'Jira', category: 'Project Management', vendor: 'Atlassian' },
      'clickup.com': { name: 'ClickUp', category: 'Project Management', vendor: 'ClickUp' },
      'basecamp.com': { name: 'Basecamp', category: 'Project Management', vendor: 'Basecamp' },
      'linear.app': { name: 'Linear', category: 'Project Management', vendor: 'Linear' },
      
      // Analytics & Marketing
      'analytics.google.com': { name: 'Google Analytics', category: 'Analytics', vendor: 'Google' },
      'mixpanel.com': { name: 'Mixpanel', category: 'Analytics', vendor: 'Mixpanel' },
      'amplitude.com': { name: 'Amplitude', category: 'Analytics', vendor: 'Amplitude' },
      'mailchimp.com': { name: 'Mailchimp', category: 'Marketing', vendor: 'Mailchimp' },
      'hubspot.com': { name: 'HubSpot', category: 'Marketing', vendor: 'HubSpot' },
      'sendgrid.com': { name: 'SendGrid', category: 'Marketing', vendor: 'Twilio' },
      
      // CRM & Support
      'salesforce.com': { name: 'Salesforce', category: 'CRM', vendor: 'Salesforce' },
      'zendesk.com': { name: 'Zendesk', category: 'CRM', vendor: 'Zendesk' },
      'intercom.com': { name: 'Intercom', category: 'CRM', vendor: 'Intercom' },
      'freshdesk.com': { name: 'Freshdesk', category: 'CRM', vendor: 'Freshworks' },
      
      // Office Suite
      'docs.google.com': { name: 'Google Docs', category: 'Office Suite', vendor: 'Google' },
      'sheets.google.com': { name: 'Google Sheets', category: 'Office Suite', vendor: 'Google' },
      'office.com': { name: 'Microsoft 365', category: 'Office Suite', vendor: 'Microsoft' },
      
      // Payment & Finance
      'stripe.com': { name: 'Stripe', category: 'Payment', vendor: 'Stripe' },
      'paypal.com': { name: 'PayPal', category: 'Payment', vendor: 'PayPal' },
      'quickbooks.intuit.com': { name: 'QuickBooks', category: 'Finance', vendor: 'Intuit' },
      
      // HR & Recruiting
      'linkedin.com': { name: 'LinkedIn', category: 'HR', vendor: 'Microsoft' },
      'greenhouse.io': { name: 'Greenhouse', category: 'HR', vendor: 'Greenhouse' },
      'lever.co': { name: 'Lever', category: 'HR', vendor: 'Lever' },
      'gusto.com': { name: 'Gusto', category: 'HR', vendor: 'Gusto' },
      'bamboohr.com': { name: 'BambooHR', category: 'HR', vendor: 'BambooHR' },
      
      // Security
      'lastpass.com': { name: 'LastPass', category: 'Security', vendor: 'LastPass' },
      '1password.com': { name: '1Password', category: 'Security', vendor: '1Password' },
      'okta.com': { name: 'Okta', category: 'Security', vendor: 'Okta' },
    };
    
    this.visitData = new Map(); // domain -> { visits: [], totalTime: 0 }
  }

  /**
   * Get browser database paths for different OS
   */
  getBrowserPaths() {
    const paths = {
      chrome: [],
      firefox: [],
      edge: [],
      safari: []
    };
    
    if (this.platform === 'darwin') {
      // macOS
      paths.chrome.push(path.join(this.homeDir, 'Library/Application Support/Google/Chrome/Default/History'));
      paths.firefox.push(path.join(this.homeDir, 'Library/Application Support/Firefox/Profiles'));
      paths.edge.push(path.join(this.homeDir, 'Library/Application Support/Microsoft Edge/Default/History'));
      paths.safari.push(path.join(this.homeDir, 'Library/Safari/History.db'));
    } else if (this.platform === 'win32') {
      // Windows
      const appData = path.join(this.homeDir, 'AppData/Local');
      paths.chrome.push(path.join(appData, 'Google/Chrome/User Data/Default/History'));
      paths.firefox.push(path.join(appData, 'Mozilla/Firefox/Profiles'));
      paths.edge.push(path.join(appData, 'Microsoft/Edge/User Data/Default/History'));
    } else if (this.platform === 'linux') {
      // Linux
      paths.chrome.push(path.join(this.homeDir, '.config/google-chrome/Default/History'));
      paths.firefox.push(path.join(this.homeDir, '.mozilla/firefox'));
      paths.edge.push(path.join(this.homeDir, '.config/microsoft-edge/Default/History'));
    }
    
    return paths;
  }

  /**
   * Scan browser history for SaaS usage
   * @param {number} hoursBack - Hours of history to scan (default: 24)
   */
  async scanBrowserHistory(hoursBack = 24) {
    console.log(`🌐 Scanning browser history (last ${hoursBack} hours)...`);
    
    const results = {
      chrome: await this.scanChrome(hoursBack),
      firefox: await this.scanFirefox(hoursBack),
      edge: await this.scanEdge(hoursBack),
      safari: await this.scanSafari(hoursBack)
    };
    
    // Aggregate results
    this.aggregateVisits(results);
    
    return this.getUsageSummary();
  }

  /**
   * Scan Chrome history
   */
  async scanChrome(hoursBack) {
    const visits = [];
    
    for (const historyPath of this.browserPaths.chrome) {
      try {
        // Check if history file exists
        await fs.access(historyPath);
        
        // Copy the history file (Chrome locks it)
        const tempPath = path.join(os.tmpdir(), `chrome-history-${Date.now()}.db`);
        await fs.copyFile(historyPath, tempPath);
        
        // Query the database
        const data = await this.queryHistoryDB(tempPath, hoursBack);
        visits.push(...data);
        
        // Clean up
        await fs.unlink(tempPath);
        
      } catch (error) {
        console.log('Chrome history not accessible:', error.message);
      }
    }
    
    return visits;
  }

  /**
   * Scan Firefox history
   */
  async scanFirefox(hoursBack) {
    const visits = [];
    
    for (const profilesDir of this.browserPaths.firefox) {
      try {
        // Check if profiles directory exists
        await fs.access(profilesDir);
        
        // Find profile directories
        const profiles = await fs.readdir(profilesDir);
        
        for (const profile of profiles) {
          if (!profile.endsWith('.default') && !profile.endsWith('.default-release')) continue;
          
          const placesPath = path.join(profilesDir, profile, 'places.sqlite');
          
          try {
            await fs.access(placesPath);
            
            // Copy the history file
            const tempPath = path.join(os.tmpdir(), `firefox-history-${Date.now()}.db`);
            await fs.copyFile(placesPath, tempPath);
            
            // Query the database (Firefox uses different schema)
            const data = await this.queryFirefoxDB(tempPath, hoursBack);
            visits.push(...data);
            
            // Clean up
            await fs.unlink(tempPath);
            
          } catch (error) {
            console.log('Firefox profile history not accessible:', error.message);
          }
        }
        
      } catch (error) {
        console.log('Firefox history not accessible:', error.message);
      }
    }
    
    return visits;
  }

  /**
   * Scan Edge history
   */
  async scanEdge(hoursBack) {
    const visits = [];
    
    for (const historyPath of this.browserPaths.edge) {
      try {
        await fs.access(historyPath);
        
        const tempPath = path.join(os.tmpdir(), `edge-history-${Date.now()}.db`);
        await fs.copyFile(historyPath, tempPath);
        
        const data = await this.queryHistoryDB(tempPath, hoursBack);
        visits.push(...data);
        
        await fs.unlink(tempPath);
        
      } catch (error) {
        console.log('Edge history not accessible:', error.message);
      }
    }
    
    return visits;
  }

  /**
   * Scan Safari history (macOS only)
   */
  async scanSafari(hoursBack) {
    if (this.platform !== 'darwin') return [];
    
    const visits = [];
    
    for (const historyPath of this.browserPaths.safari) {
      try {
        await fs.access(historyPath);
        
        const tempPath = path.join(os.tmpdir(), `safari-history-${Date.now()}.db`);
        await fs.copyFile(historyPath, tempPath);
        
        const data = await this.querySafariDB(tempPath, hoursBack);
        visits.push(...data);
        
        await fs.unlink(tempPath);
        
      } catch (error) {
        console.log('Safari history not accessible:', error.message);
      }
    }
    
    return visits;
  }

  /**
   * Query Chrome/Edge history database
   */
  async queryHistoryDB(dbPath, hoursBack) {
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
        if (err) {
          reject(err);
          return;
        }
      });
      
      const cutoffTime = Date.now() - (hoursBack * 60 * 60 * 1000);
      const chromeCutoff = (cutoffTime * 1000) + 11644473600000000; // Chrome's epoch
      
      const query = `
        SELECT url, title, visit_count, last_visit_time
        FROM urls
        WHERE last_visit_time > ?
        ORDER BY last_visit_time DESC
      `;
      
      db.all(query, [chromeCutoff], (err, rows) => {
        db.close();
        
        if (err) {
          reject(err);
          return;
        }
        
        const visits = rows.map(row => ({
          url: row.url,
          title: row.title,
          visitCount: row.visit_count,
          lastVisit: new Date((row.last_visit_time - 11644473600000000) / 1000)
        }));
        
        resolve(visits);
      });
    });
  }

  /**
   * Query Firefox history database
   */
  async queryFirefoxDB(dbPath, hoursBack) {
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
        if (err) {
          reject(err);
          return;
        }
      });
      
      const cutoffTime = Date.now() - (hoursBack * 60 * 60 * 1000);
      const firefoxCutoff = cutoffTime * 1000; // Firefox uses microseconds
      
      const query = `
        SELECT p.url, p.title, p.visit_count, h.visit_date
        FROM moz_places p
        JOIN moz_historyvisits h ON p.id = h.place_id
        WHERE h.visit_date > ?
        ORDER BY h.visit_date DESC
      `;
      
      db.all(query, [firefoxCutoff], (err, rows) => {
        db.close();
        
        if (err) {
          reject(err);
          return;
        }
        
        const visits = rows.map(row => ({
          url: row.url,
          title: row.title,
          visitCount: row.visit_count,
          lastVisit: new Date(row.visit_date / 1000)
        }));
        
        resolve(visits);
      });
    });
  }

  /**
   * Query Safari history database
   */
  async querySafariDB(dbPath, hoursBack) {
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
        if (err) {
          reject(err);
          return;
        }
      });
      
      const cutoffTime = Date.now() - (hoursBack * 60 * 60 * 1000);
      const safariCutoff = cutoffTime / 1000 - 978307200; // Safari's epoch (Jan 1, 2001)
      
      const query = `
        SELECT i.url, v.title, v.visit_count, v.visit_time
        FROM history_items i
        JOIN history_visits v ON i.id = v.history_item
        WHERE v.visit_time > ?
        ORDER BY v.visit_time DESC
      `;
      
      db.all(query, [safariCutoff], (err, rows) => {
        db.close();
        
        if (err) {
          reject(err);
          return;
        }
        
        const visits = rows.map(row => ({
          url: row.url,
          title: row.title,
          visitCount: row.visit_count,
          lastVisit: new Date((row.visit_time + 978307200) * 1000)
        }));
        
        resolve(visits);
      });
    });
  }

  /**
   * Aggregate visit data from all browsers
   */
  aggregateVisits(results) {
    this.visitData.clear();
    
    for (const [browser, visits] of Object.entries(results)) {
      for (const visit of visits) {
        // Check if URL matches a SaaS pattern
        const saasInfo = this.matchSaasPattern(visit.url);
        
        if (saasInfo) {
          const key = saasInfo.name;
          
          if (!this.visitData.has(key)) {
            this.visitData.set(key, {
              ...saasInfo,
              visits: [],
              totalVisits: 0,
              browsers: new Set()
            });
          }
          
          const data = this.visitData.get(key);
          data.visits.push({
            url: visit.url,
            title: visit.title,
            timestamp: visit.lastVisit,
            browser
          });
          data.totalVisits += visit.visitCount || 1;
          data.browsers.add(browser);
        }
      }
    }
  }

  /**
   * Match URL against SaaS patterns
   */
  matchSaasPattern(url) {
    try {
      const urlObj = new URL(url);
      const hostname = urlObj.hostname.toLowerCase();
      
      for (const [pattern, info] of Object.entries(this.saasPatterns)) {
        if (hostname.includes(pattern)) {
          return info;
        }
      }
    } catch (error) {
      // Invalid URL
    }
    
    return null;
  }

  /**
   * Get usage summary
   */
  getUsageSummary() {
    const summary = [];
    
    for (const [name, data] of this.visitData.entries()) {
      summary.push({
        name: data.name,
        category: data.category,
        vendor: data.vendor,
        totalVisits: data.totalVisits,
        uniqueDays: this.getUniqueDays(data.visits),
        lastVisit: data.visits.length > 0 ? data.visits[data.visits.length - 1].timestamp : null,
        browsers: Array.from(data.browsers)
      });
    }
    
    // Sort by total visits
    return summary.sort((a, b) => b.totalVisits - a.totalVisits);
  }

  /**
   * Get unique days of visits
   */
  getUniqueDays(visits) {
    const days = new Set();
    for (const visit of visits) {
      const day = visit.timestamp.toISOString().split('T')[0];
      days.add(day);
    }
    return days.size;
  }

  /**
   * Get usage by category
   */
  getUsageByCategory() {
    const byCategory = {};
    
    for (const [name, data] of this.visitData.entries()) {
      if (!byCategory[data.category]) {
        byCategory[data.category] = {
          totalVisits: 0,
          apps: []
        };
      }
      byCategory[data.category].totalVisits += data.totalVisits;
      byCategory[data.category].apps.push({
        name: data.name,
        visits: data.totalVisits
      });
    }
    
    return byCategory;
  }

  /**
   * Get usage by vendor
   */
  getUsageByVendor() {
    const byVendor = {};
    
    for (const [name, data] of this.visitData.entries()) {
      if (!byVendor[data.vendor]) {
        byVendor[data.vendor] = {
          totalVisits: 0,
          apps: []
        };
      }
      byVendor[data.vendor].totalVisits += data.totalVisits;
      byVendor[data.vendor].apps.push({
        name: data.name,
        visits: data.totalVisits
      });
    }
    
    return byVendor;
  }
}

module.exports = BrowserMonitor;
