const ical = require('ical');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const { exec } = require('child_process');
const util = require('util');

const execPromise = util.promisify(exec);

class CalendarSync {
  constructor(apiClient) {
    this.apiClient = apiClient;
    this.isMonitoring = false;
    this.platform = process.platform;
  }

  async startMonitoring() {
    if (this.isMonitoring) return;
    this.isMonitoring = true;

    console.log('📅 Starting calendar monitoring...');

    // Initial sync
    await this.syncCalendar();

    // Monitor for changes every hour
    this.monitoringInterval = setInterval(async () => {
      await this.syncCalendar();
    }, 60 * 60 * 1000);
  }

  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    this.isMonitoring = false;
  }

  async syncCalendar() {
    try {
      const events = await this.getEvents();
      
      // Find subscription renewal events
      const renewalEvents = events.filter(event => 
        this.isRenewalEvent(event)
      );

      console.log(`📅 Found ${renewalEvents.length} renewal events`);

      // Create reminders for upcoming renewals
      for (const event of renewalEvents) {
        await this.createRenewalReminder(event);
      }

      return renewalEvents;
    } catch (error) {
      console.error('Calendar sync error:', error.message);
      return [];
    }
  }

  async getEvents(options = {}) {
    const { startDate, endDate } = options;
    const start = startDate || new Date();
    const end = endDate || new Date(Date.now() + 90 * 24 * 60 * 60 * 1000); // 90 days

    switch (this.platform) {
      case 'darwin':
        return await this.getMacCalendarEvents(start, end);

      case 'win32':
        return await this.getWindowsCalendarEvents(start, end);

      case 'linux':
        return await this.getLinuxCalendarEvents(start, end);

      default:
        return [];
    }
  }

  async getMacCalendarEvents(startDate, endDate) {
    const events = [];

    try {
      // Use macOS Calendar.app SQLite database
      const calendarDbPath = path.join(
        os.homedir(),
        'Library/Calendars'
      );

      // Alternative: Use AppleScript to query Calendar.app
      const appleScript = `
        tell application "Calendar"
          set startDate to date "${startDate.toISOString()}"
          set endDate to date "${endDate.toISOString()}"
          set eventList to events of calendar 1 whose start date ≥ startDate and start date ≤ endDate
          
          set output to ""
          repeat with theEvent in eventList
            set output to output & summary of theEvent & "|" & start date of theEvent & "|" & description of theEvent & "\\n"
          end repeat
          
          return output
        end tell
      `;

      const { stdout } = await execPromise(
        `osascript -e '${appleScript.replace(/'/g, "\\'")}'`
      );

      const lines = stdout.trim().split('\n');
      
      for (const line of lines) {
        const [summary, date, description] = line.split('|');
        if (summary) {
          events.push({
            summary: summary.trim(),
            start: new Date(date.trim()),
            description: description?.trim() || ''
          });
        }
      }
    } catch (error) {
      console.error('Mac Calendar access error:', error.message);
      console.log('💡 Tip: Grant Calendar access in System Preferences > Security & Privacy');
    }

    return events;
  }

  async getWindowsCalendarEvents(startDate, endDate) {
    const events = [];

    try {
      // Windows Calendar stores events in Windows.ApplicationModel.Appointments
      // This requires PowerShell to access
      const powershellScript = `
        Add-Type -AssemblyName Windows.ApplicationModel
        $start = [DateTime]::Parse("${startDate.toISOString()}")
        $end = [DateTime]::Parse("${endDate.toISOString()}")
        
        $store = [Windows.ApplicationModel.Appointments.AppointmentManager]::GetForUser($null).RequestStoreAsync([Windows.ApplicationModel.Appointments.AppointmentStoreAccessType]::AllCalendarsReadOnly).GetResults()
        $appointments = $store.FindAppointmentsAsync($start, $end.Subtract($start)).GetResults()
        
        foreach ($appt in $appointments) {
          Write-Output "$($appt.Subject)|$($appt.StartTime)|$($appt.Details)"
        }
      `;

      const { stdout } = await execPromise(
        `powershell -Command "${powershellScript.replace(/"/g, '\\"')}"`
      );

      const lines = stdout.trim().split('\n');
      
      for (const line of lines) {
        const [subject, startTime, details] = line.split('|');
        if (subject) {
          events.push({
            summary: subject.trim(),
            start: new Date(startTime.trim()),
            description: details?.trim() || ''
          });
        }
      }
    } catch (error) {
      console.error('Windows Calendar access error:', error.message);
    }

    return events;
  }

  async getLinuxCalendarEvents(startDate, endDate) {
    const events = [];

    try {
      // Linux typically uses .ics files in various locations
      const icsLocations = [
        path.join(os.homedir(), '.local/share/evolution/calendar'),
        path.join(os.homedir(), '.thunderbird/*/calendar-data'),
        path.join(os.homedir(), 'ownCloud/calendars'),
        path.join(os.homedir(), 'Nextcloud/calendars')
      ];

      for (const location of icsLocations) {
        try {
          const files = await this.findICSFiles(location);
          
          for (const file of files) {
            const content = await fs.readFile(file, 'utf-8');
            const parsed = ical.parseICS(content);

            for (const uid in parsed) {
              const event = parsed[uid];
              if (event.type === 'VEVENT') {
                const eventStart = new Date(event.start);
                
                if (eventStart >= startDate && eventStart <= endDate) {
                  events.push({
                    summary: event.summary,
                    start: eventStart,
                    description: event.description || '',
                    location: event.location || ''
                  });
                }
              }
            }
          }
        } catch (error) {
          continue;
        }
      }
    } catch (error) {
      console.error('Linux Calendar access error:', error.message);
    }

    return events;
  }

  async findICSFiles(basePath) {
    const files = [];

    async function walk(dir) {
      try {
        const items = await fs.readdir(dir, { withFileTypes: true });

        for (const item of items) {
          const fullPath = path.join(dir, item.name);

          if (item.isDirectory()) {
            await walk(fullPath);
          } else if (item.isFile() && item.name.endsWith('.ics')) {
            files.push(fullPath);
          }
        }
      } catch (error) {
        // Skip inaccessible directories
      }
    }

    await walk(basePath);
    return files;
  }

  isRenewalEvent(event) {
    const renewalKeywords = [
      'renewal', 'renew', 'subscription', 'billing', 'payment due',
      'auto-renew', 'expires', 'expiration', 'trial ends'
    ];

    const summary = (event.summary || '').toLowerCase();
    const description = (event.description || '').toLowerCase();

    return renewalKeywords.some(kw => 
      summary.includes(kw) || description.includes(kw)
    );
  }

  async createRenewalReminder(event) {
    try {
      // Send notification 3 days before renewal
      const daysUntilRenewal = Math.ceil(
        (event.start.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
      );

      if (daysUntilRenewal <= 3 && daysUntilRenewal >= 0) {
        // Create backend reminder
        await this.apiClient.createCalendarEvent({
          title: event.summary,
          date: event.start,
          type: 'renewal',
          description: event.description,
          days_before_reminder: 3
        });

        console.log(`⏰ Created reminder for: ${event.summary}`);
      }
    } catch (error) {
      console.error('Create reminder error:', error.message);
    }
  }
}

module.exports = CalendarSync;
