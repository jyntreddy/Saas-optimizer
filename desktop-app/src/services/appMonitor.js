const { exec } = require('child_process');
const { promisify } = require('util');
const os = require('os');

const execAsync = promisify(exec);

/**
 * Application Monitor Service
 * Tracks which applications are running and their usage duration
 * Focuses on SaaS applications and productivity tools
 */
class AppMonitor {
  constructor() {
    this.platform = os.platform();
    this.runningApps = new Map(); // appName -> { startTime, totalDuration, category }
    this.previousApps = new Set();
    this.monitorInterval = null;
    
    // Known SaaS applications to track
    this.saasApps = {
      // Communication
      'Slack': { category: 'Communication', vendor: 'Slack' },
      'Microsoft Teams': { category: 'Communication', vendor: 'Microsoft' },
      'Zoom': { category: 'Communication', vendor: 'Zoom' },
      'Discord': { category: 'Communication', vendor: 'Discord' },
      'Skype': { category: 'Communication', vendor: 'Microsoft' },
      
      // Productivity
      'Notion': { category: 'Productivity', vendor: 'Notion' },
      'Todoist': { category: 'Productivity', vendor: 'Todoist' },
      'Trello': { category: 'Productivity', vendor: 'Atlassian' },
      'Asana': { category: 'Productivity', vendor: 'Asana' },
      'Monday': { category: 'Productivity', vendor: 'Monday.com' },
      
      // Development
      'GitHub Desktop': { category: 'Development', vendor: 'GitHub' },
      'GitKraken': { category: 'Development', vendor: 'GitKraken' },
      'Docker': { category: 'Development', vendor: 'Docker' },
      'Postman': { category: 'Development', vendor: 'Postman' },
      'Visual Studio Code': { category: 'Development', vendor: 'Microsoft' },
      'JetBrains': { category: 'Development', vendor: 'JetBrains' },
      
      // Design
      'Figma': { category: 'Design', vendor: 'Figma' },
      'Sketch': { category: 'Design', vendor: 'Sketch' },
      'Adobe Creative Cloud': { category: 'Design', vendor: 'Adobe' },
      'Canva': { category: 'Design', vendor: 'Canva' },
      
      // Cloud Storage
      'Dropbox': { category: 'Cloud Storage', vendor: 'Dropbox' },
      'Google Drive': { category: 'Cloud Storage', vendor: 'Google' },
      'OneDrive': { category: 'Cloud Storage', vendor: 'Microsoft' },
      'Box': { category: 'Cloud Storage', vendor: 'Box' },
      
      // Project Management
      'Jira': { category: 'Project Management', vendor: 'Atlassian' },
      'ClickUp': { category: 'Project Management', vendor: 'ClickUp' },
      'Basecamp': { category: 'Project Management', vendor: 'Basecamp' },
      
      // Analytics & Marketing
      'Google Analytics': { category: 'Analytics', vendor: 'Google' },
      'Mixpanel': { category: 'Analytics', vendor: 'Mixpanel' },
      'Mailchimp': { category: 'Marketing', vendor: 'Mailchimp' },
      'HubSpot': { category: 'Marketing', vendor: 'HubSpot' },
      
      // CRM
      'Salesforce': { category: 'CRM', vendor: 'Salesforce' },
      'Zendesk': { category: 'CRM', vendor: 'Zendesk' },
      'Intercom': { category: 'CRM', vendor: 'Intercom' },
      
      // Office Suite
      'Microsoft Word': { category: 'Office Suite', vendor: 'Microsoft' },
      'Microsoft Excel': { category: 'Office Suite', vendor: 'Microsoft' },
      'Microsoft PowerPoint': { category: 'Office Suite', vendor: 'Microsoft' },
      'Google Chrome': { category: 'Browser', vendor: 'Google' },
      'Safari': { category: 'Browser', vendor: 'Apple' },
      'Firefox': { category: 'Browser', vendor: 'Mozilla' },
      'Edge': { category: 'Browser', vendor: 'Microsoft' },
    };
  }

  /**
   * Start monitoring applications
   * @param {number} intervalMs - Monitoring interval in milliseconds (default: 5 seconds)
   */
  startMonitoring(intervalMs = 5000) {
    console.log('🔍 Starting application monitoring...');
    
    // Initial scan
    this.scanRunningApps();
    
    // Periodic scanning
    this.monitorInterval = setInterval(() => {
      this.scanRunningApps();
    }, intervalMs);
  }

  /**
   * Stop monitoring applications
   */
  stopMonitoring() {
    if (this.monitorInterval) {
      clearInterval(this.monitorInterval);
      this.monitorInterval = null;
      console.log('🛑 Application monitoring stopped');
    }
  }

  /**
   * Scan currently running applications
   */
  async scanRunningApps() {
    try {
      let apps = [];
      
      if (this.platform === 'darwin') {
        apps = await this.getMacRunningApps();
      } else if (this.platform === 'win32') {
        apps = await this.getWindowsRunningApps();
      } else if (this.platform === 'linux') {
        apps = await this.getLinuxRunningApps();
      }
      
      const currentApps = new Set(apps);
      const now = Date.now();
      
      // Track newly started apps
      for (const app of currentApps) {
        if (!this.previousApps.has(app) && this.isSaasApp(app)) {
          this.runningApps.set(app, {
            startTime: now,
            totalDuration: this.runningApps.get(app)?.totalDuration || 0,
            category: this.getCategoryForApp(app),
            vendor: this.getVendorForApp(app)
          });
          console.log(`✅ Started tracking: ${app}`);
        }
      }
      
      // Track stopped apps
      for (const app of this.previousApps) {
        if (!currentApps.has(app) && this.runningApps.has(app)) {
          const appData = this.runningApps.get(app);
          const duration = now - appData.startTime;
          appData.totalDuration += duration;
          appData.lastStopped = now;
          delete appData.startTime; // Mark as not currently running
          console.log(`⏸️  Stopped tracking: ${app} (Duration: ${Math.round(duration / 1000)}s)`);
        }
      }
      
      this.previousApps = currentApps;
      
    } catch (error) {
      console.error('Error scanning running apps:', error);
    }
  }

  /**
   * Get running applications on macOS
   */
  async getMacRunningApps() {
    try {
      const { stdout } = await execAsync('ps -axo comm | grep ".app/Contents/MacOS" | sed "s/.*\\/\\(.*\\)\\.app\\/Contents\\/MacOS\\/.*/\\1/" | sort -u');
      return stdout.trim().split('\n').filter(app => app.length > 0);
    } catch (error) {
      console.error('Error getting macOS apps:', error);
      return [];
    }
  }

  /**
   * Get running applications on Windows
   */
  async getWindowsRunningApps() {
    try {
      const { stdout } = await execAsync('powershell "Get-Process | Where-Object {$_.MainWindowTitle -ne \'\'} | Select-Object -ExpandProperty ProcessName | Sort-Object -Unique"');
      return stdout.trim().split('\r\n').filter(app => app.length > 0);
    } catch (error) {
      console.error('Error getting Windows apps:', error);
      return [];
    }
  }

  /**
   * Get running applications on Linux
   */
  async getLinuxRunningApps() {
    try {
      const { stdout } = await execAsync('ps -eo comm --sort comm | uniq');
      return stdout.trim().split('\n').filter(app => app.length > 0);
    } catch (error) {
      console.error('Error getting Linux apps:', error);
      return [];
    }
  }

  /**
   * Check if an app is a known SaaS application
   */
  isSaasApp(appName) {
    return Object.keys(this.saasApps).some(saas => 
      appName.toLowerCase().includes(saas.toLowerCase())
    );
  }

  /**
   * Get category for an application
   */
  getCategoryForApp(appName) {
    for (const [saas, data] of Object.entries(this.saasApps)) {
      if (appName.toLowerCase().includes(saas.toLowerCase())) {
        return data.category;
      }
    }
    return 'Other';
  }

  /**
   * Get vendor for an application
   */
  getVendorForApp(appName) {
    for (const [saas, data] of Object.entries(this.saasApps)) {
      if (appName.toLowerCase().includes(saas.toLowerCase())) {
        return data.vendor;
      }
    }
    return 'Unknown';
  }

  /**
   * Get usage summary for all tracked apps
   */
  getUsageSummary() {
    const summary = [];
    const now = Date.now();
    
    for (const [appName, data] of this.runningApps.entries()) {
      let totalDuration = data.totalDuration;
      
      // Add current session duration if app is still running
      if (data.startTime) {
        totalDuration += (now - data.startTime);
      }
      
      summary.push({
        appName,
        category: data.category,
        vendor: data.vendor,
        totalDuration: Math.round(totalDuration / 1000), // in seconds
        isCurrentlyRunning: !!data.startTime,
        lastActivity: data.startTime || data.lastStopped
      });
    }
    
    // Sort by total duration (descending)
    return summary.sort((a, b) => b.totalDuration - a.totalDuration);
  }

  /**
   * Get usage grouped by category
   */
  getUsageByCategory() {
    const summary = this.getUsageSummary();
    const byCategory = {};
    
    for (const app of summary) {
      if (!byCategory[app.category]) {
        byCategory[app.category] = {
          totalDuration: 0,
          apps: []
        };
      }
      byCategory[app.category].totalDuration += app.totalDuration;
      byCategory[app.category].apps.push(app);
    }
    
    return byCategory;
  }

  /**
   * Get usage grouped by vendor
   */
  getUsageByVendor() {
    const summary = this.getUsageSummary();
    const byVendor = {};
    
    for (const app of summary) {
      if (!byVendor[app.vendor]) {
        byVendor[app.vendor] = {
          totalDuration: 0,
          apps: []
        };
      }
      byVendor[app.vendor].totalDuration += app.totalDuration;
      byVendor[app.vendor].apps.push(app);
    }
    
    return byVendor;
  }

  /**
   * Reset all tracking data
   */
  reset() {
    this.runningApps.clear();
    this.previousApps.clear();
    console.log('🔄 Application monitoring data reset');
  }

  /**
   * Get currently running SaaS apps
   */
  getCurrentlyRunningApps() {
    const running = [];
    for (const [appName, data] of this.runningApps.entries()) {
      if (data.startTime) {
        running.push({
          appName,
          category: data.category,
          vendor: data.vendor,
          duration: Math.round((Date.now() - data.startTime) / 1000)
        });
      }
    }
    return running;
  }
}

module.exports = AppMonitor;
