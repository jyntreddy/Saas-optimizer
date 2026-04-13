/**
 * Usage Analytics Aggregator
 * Combines data from AppMonitor, BrowserMonitor, EmailReader, and CalendarSync
 * to generate comprehensive SaaS usage insights
 */
class UsageAnalytics {
  constructor() {
    this.appMonitor = null;
    this.browserMonitor = null;
    this.emailData = [];
    this.calendarData = [];
  }

  /**
   * Set monitoring services
   */
  setMonitors(appMonitor, browserMonitor) {
    this.appMonitor = appMonitor;
    this.browserMonitor = browserMonitor;
  }

  /**
   * Add email receipt data
   */
  addEmailData(receipts) {
    this.emailData = receipts;
  }

  /**
   * Add calendar event data
   */
  addCalendarData(events) {
    this.calendarData = events;
  }

  /**
   * Generate comprehensive dashboard data
   */
  async generateDashboard() {
    console.log('📊 Generating dashboard analytics...');
    
    // Get data from all sources
    const appUsage = this.appMonitor ? this.appMonitor.getUsageSummary() : [];
    const browserUsage = this.browserMonitor ? this.browserMonitor.getUsageSummary() : [];
    
    // Combine and correlate data
    const subscriptions = this.detectSubscriptions(appUsage, browserUsage, this.emailData);
    const spending = this.calculateSpending(this.emailData);
    const recommendations = this.generateRecommendations(subscriptions, appUsage, browserUsage);
    const teamUsage = this.analyzeTeamUsage(subscriptions);
    const saasScore = this.calculateSaasScore(subscriptions, spending, appUsage, browserUsage);
    
    return {
      overview: {
        totalSubscriptions: subscriptions.length,
        activeSubscriptions: subscriptions.filter(s => 
s.isActive).length,
        monthlySpend: spending.monthly,
        annualSpend: spending.annual,
        unusedSubscriptions: subscriptions.filter(s => !s.isUsed).length,
        potentialSavings: this.calculatePotentialSavings(subscriptions),
        saasScore: saasScore
      },
      subscriptions,
      spending,
      recommendations,
      teamUsage,
      analytics: {
        usageByCategory: this.getUsageByCategory(appUsage, browserUsage),
        usageByVendor: this.getUsageByVendor(appUsage, browserUsage),
        costPerUsage: this.calculateCostPerUsage(subscriptions, appUsage, browserUsage),
        renewalCalendar: this.getRenewalCalendar(subscriptions, this.calendarData)
      }
    };
  }

  /**
   * Detect subscriptions from all data sources
   */
  detectSubscriptions(appUsage, browserUsage, emailData) {
    const subscriptionMap = new Map();
    
    // From email receipts
    for (const receipt of emailData) {
      const vendor = receipt.vendor || receipt.from;
      
      if (!subscriptionMap.has(vendor)) {
        subscriptionMap.set(vendor, {
          vendor,
          name: receipt.subscriptionType || vendor,
          category: receipt.category || 'Unknown',
          cost: 0,
          billing: 'monthly',
          isActive: true,
          isUsed: false,
          lastPayment: null,
          nextRenewal: null,
          usageData: {
            appDuration: 0,
            browserVisits: 0,
            lastAppUsage: null,
            lastBrowserUsage: null
          },
          source: []
        });
      }
      
      const sub = subscriptionMap.get(vendor);
      sub.cost += receipt.amount || 0;
      sub.lastPayment = receipt.date;
      sub.source.push('email');
    }
    
    // From app usage
    for (const app of appUsage) {
      if (!subscriptionMap.has(app.vendor)) {
        subscriptionMap.set(app.vendor, {
          vendor: app.vendor,
          name: app.appName,
          category: app.category,
          cost: 0,
          billing: 'unknown',
          isActive: true,
          isUsed: true,
          usageData: {
            appDuration: 0,
            browserVisits: 0,
            lastAppUsage: null,
            lastBrowserUsage: null
          },
          source: []
        });
      }
      
      const sub = subscriptionMap.get(app.vendor);
      sub.isUsed = true;
      sub.usageData.appDuration += app.totalDuration;
      sub.usageData.lastAppUsage = app.lastActivity;
      if (!sub.source.includes('app')) sub.source.push('app');
    }
    
    // From browser usage
    for (const site of browserUsage) {
      if (!subscriptionMap.has(site.vendor)) {
        subscriptionMap.set(site.vendor, {
          vendor: site.vendor,
          name: site.name,
          category: site.category,
          cost: 0,
          billing: 'unknown',
          isActive: true,
          isUsed: true,
          usageData: {
            appDuration: 0,
            browserVisits: 0,
            lastAppUsage: null,
            lastBrowserUsage: null
          },
          source: []
        });
      }
      
      const sub = subscriptionMap.get(site.vendor);
      sub.isUsed = true;
      sub.usageData.browserVisits += site.totalVisits;
      sub.usageData.lastBrowserUsage = site.lastVisit;
      if (!sub.source.includes('browser')) sub.source.push('browser');
    }
    
    return Array.from(subscriptionMap.values());
  }

  /**
   * Calculate spending breakdown
   */
  calculateSpending(emailData) {
    let monthly = 0;
    let annual = 0;
    const byCategory = {};
    const byVendor = {};
    const history = [];
    
    for (const receipt of emailData) {
      const amount = receipt.amount || 0;
      const vendor = receipt.vendor || receipt.from;
      const category = receipt.category || 'Unknown';
      
      // Estimate monthly/annual
      if (receipt.billingPeriod === 'monthly' || !receipt.billingPeriod) {
        monthly += amount;
        annual += amount * 12;
      } else if (receipt.billingPeriod === 'annual') {
        annual += amount;
        monthly += amount / 12;
      }
      
      // By category
      byCategory[category] = (byCategory[category] || 0) + amount;
      
      // By vendor
      byVendor[vendor] = (byVendor[vendor] || 0) + amount;
      
      // History
      history.push({
        date: receipt.date,
        vendor,
        amount,
        category
      });
    }
    
    // Sort history by date
    history.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    return {
      monthly,
      annual,
      byCategory,
      byVendor,
      history: history.slice(0, 50) // Last 50 transactions
    };
  }

  /**
   * Generate cost-saving recommendations
   */
  generateRecommendations(subscriptions, appUsage, browserUsage) {
    const recommendations = [];
    
    // 1. Unused subscriptions
    const unused = subscriptions.filter(s => !s.isUsed && s.cost > 0);
    for (const sub of unused) {
      recommendations.push({
        type: 'cancel',
        priority: 'high',
        title: `Cancel unused ${sub.vendor}`,
        description: `You haven't used ${sub.vendor} recently but are still paying $${sub.cost.toFixed(2)}/month`,
        potentialSaving: sub.cost,
        action: 'cancel',
        subscription: sub.vendor
      });
    }
    
    // 2. Low usage subscriptions
    const lowUsage = subscriptions.filter(s => {
      const usage = s.usageData;
      const totalUsage = usage.appDuration + (usage.browserVisits * 60); // Assume 1 min per visit
      return s.isUsed && totalUsage < 3600 && s.cost > 0; // Less than 1 hour/month
    });
    
    for (const sub of lowUsage) {
      recommendations.push({
        type: 'downgrade',
        priority: 'medium',
        title: `Consider downgrading ${sub.vendor}`,
        description: `Low usage detected for ${sub.vendor}. You might save money with a lower tier.`,
        potentialSaving: sub.cost * 0.3, // Estimate 30% savings
        action: 'downgrade',
        subscription: sub.vendor
      });
    }
    
    // 3. Duplicate services
    const byCategory = {};
    for (const sub of subscriptions) {
      if (!byCategory[sub.category]) {
        byCategory[sub.category] = [];
      }
      byCategory[sub.category].push(sub);
    }
    
    for (const [category, subs] of Object.entries(byCategory)) {
      if (subs.length > 1 && subs.filter(s => s.cost > 0).length > 1) {
        const totalCost = subs.reduce((sum, s) => sum + s.cost, 0);
        recommendations.push({
          type: 'consolidate',
          priority: 'medium',
          title: `Consolidate ${category} tools`,
          description: `You're using ${subs.length} ${category} tools (${subs.map(s => s.vendor).join(', ')}). Consider consolidating.`,
          potentialSaving: totalCost * 0.5,
          action: 'consolidate',
          subscriptions: subs.map(s => s.vendor)
        });
      }
    }
    
    // 4. Annual billing savings
    const monthlyBilling = subscriptions.filter(s => s.billing === 'monthly' && s.cost > 10);
    for (const sub of monthlyBilling) {
      recommendations.push({
        type: 'annual',
        priority: 'low',
        title: `Switch ${sub.vendor} to annual billing`,
        description: `Most SaaS tools offer 15-20% discount for annual billing`,
        potentialSaving: sub.cost * 12 * 0.17, // Estimate 17% savings
        action: 'switch-to-annual',
        subscription: sub.vendor
      });
    }
    
    // Sort by potential savings
    recommendations.sort((a, b) => b.potentialSaving - a.potentialSaving);
    
    return recommendations.slice(0, 10); // Top 10 recommendations
  }

  /**
   * Calculate potential savings
   */
  calculatePotentialSavings(subscriptions) {
    let savings = 0;
    
    // Unused subscriptions
    const unused = subscriptions.filter(s => !s.isUsed && s.cost > 0);
    savings += unused.reduce((sum, s) => sum + s.cost, 0);
    
    // Low usage (30% savings estimate)
    const lowUsage = subscriptions.filter(s => {
      const usage = s.usageData;
      const totalUsage = usage.appDuration + (usage.browserVisits * 60);
      return s.isUsed && totalUsage < 3600 && s.cost > 0;
    });
    savings += lowUsage.reduce((sum, s) => sum + s.cost * 0.3, 0);
    
    return Math.round(savings);
  }

  /**
   * Analyze team usage patterns
   */
  analyzeTeamUsage(subscriptions) {
    // This would require multi-user data in a real implementation
    // For now, return single-user data formatted for team view
    return {
      totalMembers: 1,
      activeMembers: 1,
      costPerMember: subscriptions.reduce((sum, s) => sum + s.cost, 0),
      topApps: subscriptions
        .filter(s => s.isUsed)
        .sort((a, b) => 
          (b.usageData.appDuration + b.usageData.browserVisits * 60) -
          (a.usageData.appDuration + a.usageData.browserVisits * 60)
        )
        .slice(0, 5)
        .map(s => ({
          name: s.vendor,
          users: 1,
          totalUsage: s.usageData.appDuration + (s.usageData.browserVisits * 60)
        }))
    };
  }

  /**
   * Calculate SaaS optimization score (0-100)
   */
  calculateSaasScore(subscriptions, spending, appUsage, browserUsage) {
    let score = 100;
    
    // Penalize for unused subscriptions (-10 points each)
    const unused = subscriptions.filter(s => !s.isUsed && s.cost > 0);
    score -= unused.length * 10;
    
    // Penalize for low usage subscriptions (-5 points each)
    const lowUsage = subscriptions.filter(s => {
      const usage = s.usageData;
      const totalUsage = usage.appDuration + (usage.browserVisits * 60);
      return s.isUsed && totalUsage < 3600 && s.cost > 0;
    });
    score -= lowUsage.length * 5;
    
    // Penalize for duplicate tools in same category (-7 points)
    const byCategory = {};
    for (const sub of subscriptions) {
      byCategory[sub.category] = (byCategory[sub.category] || 0) + 1;
    }
    const duplicates = Object.values(byCategory).filter(count => count > 1).length;
    score -= duplicates * 7;
    
    // Penalize for high spend/usage ratio
    const totalUsage = appUsage.reduce((sum, a) => sum + a.totalDuration, 0) +
                      browserUsage.reduce((sum, b) => sum + b.totalVisits * 60, 0);
    const spendPerHour = totalUsage > 0 ? (spending.monthly / (totalUsage / 3600)) : 0;
    if (spendPerHour > 50) score -= 10;
    else if (spendPerHour > 30) score -= 5;
    
    // Bonus for good practices
    const withAnnualBilling = subscriptions.filter(s => s.billing === 'annual').length;
    score += Math.min(withAnnualBilling * 2, 10); // Up to +10 for annual billing
    
    return Math.max(0, Math.min(100, score));
  }

  /**
   * Get usage aggregated by category
   */
  getUsageByCategory(appUsage, browserUsage) {
    const byCategory = {};
    
    for (const app of appUsage) {
      if (!byCategory[app.category]) {
        byCategory[app.category] = {
          appDuration: 0,
          browserVisits: 0,
          tools: []
        };
      }
      byCategory[app.category].appDuration += app.totalDuration;
      byCategory[app.category].tools.push({
        name: app.appName,
        type: 'app',
        usage: app.totalDuration
      });
    }
    
    for (const site of browserUsage) {
      if (!byCategory[site.category]) {
        byCategory[site.category] = {
          appDuration: 0,
          browserVisits: 0,
          tools: []
        };
      }
      byCategory[site.category].browserVisits += site.totalVisits;
      byCategory[site.category].tools.push({
        name: site.name,
        type: 'browser',
        usage: site.totalVisits
      });
    }
    
    return byCategory;
  }

  /**
   * Get usage aggregated by vendor
   */
  getUsageByVendor(appUsage, browserUsage) {
    const byVendor = {};
    
    for (const app of appUsage) {
      if (!byVendor[app.vendor]) {
        byVendor[app.vendor] = {
          appDuration: 0,
          browserVisits: 0,
          tools: []
        };
      }
      byVendor[app.vendor].appDuration += app.totalDuration;
      byVendor[app.vendor].tools.push({
        name: app.appName,
        type: 'app',
        usage: app.totalDuration
      });
    }
    
    for (const site of browserUsage) {
      if (!byVendor[site.vendor]) {
        byVendor[site.vendor] = {
          appDuration: 0,
          browserVisits: 0,
          tools: []
        };
      }
      byVendor[site.vendor].browserVisits += site.totalVisits;
      byVendor[site.vendor].tools.push({
        name: site.name,
        type: 'browser',
        usage: site.totalVisits
      });
    }
    
    return byVendor;
  }

  /**
   * Calculate cost per usage metrics
   */
  calculateCostPerUsage(subscriptions, appUsage, browserUsage) {
    const metrics = [];
    
    for (const sub of subscriptions) {
      if (sub.cost === 0) continue;
      
      const usage = sub.usageData;
      const totalUsageMinutes = (usage.appDuration / 60) + usage.browserVisits;
      
      if (totalUsageMinutes > 0) {
        metrics.push({
          vendor: sub.vendor,
          costPerHour: (sub.cost / (totalUsageMinutes / 60)).toFixed(2),
          totalCost: sub.cost,
          totalUsage: Math.round(totalUsageMinutes),
          efficiency: totalUsageMinutes / sub.cost // minutes per dollar
        });
      }
    }
    
    // Sort by cost per hour (descending - most expensive first)
    return metrics.sort((a, b) => b.costPerHour - a.costPerHour);
  }

  /**
   * Get renewal calendar from calendar events and subscriptions
   */
  getRenewalCalendar(subscriptions, calendarData) {
    const renewals = [];
    
    // From calendar events
    for (const event of calendarData) {
      renewals.push({
        date: event.date,
        vendor: event.title,
        type: 'calendar',
        amount: null
      });
    }
    
    // From subscriptions (estimate next renewal)
    for (const sub of subscriptions) {
      if (sub.lastPayment) {
        const lastPayment = new Date(sub.lastPayment);
        let nextRenewal;
        
        if (sub.billing === 'monthly') {
          nextRenewal = new Date(lastPayment);
          nextRenewal.setMonth(nextRenewal.getMonth() + 1);
        } else if (sub.billing === 'annual') {
          nextRenewal = new Date(lastPayment);
          nextRenewal.setFullYear(nextRenewal.getFullYear() + 1);
        }
        
        if (nextRenewal && nextRenewal > new Date()) {
          renewals.push({
            date: nextRenewal.toISOString(),
            vendor: sub.vendor,
            type: 'estimated',
            amount: sub.cost
          });
        }
      }
    }
    
    // Sort by date
    renewals.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    return renewals;
  }

  /**
   * Get alternative suggestions for subscriptions
   */
  generateAlternatives(subscriptions) {
    // This would ideally use an API or database of alternatives
    // For now, return some common alternatives as examples
    const alternatives = {
      'Slack': [
        { name: 'Microsoft Teams', savings: 0, reason: 'Included with Office 365' },
        { name: 'Discord', savings: 15, reason: 'Free for teams' },
        { name: 'Mattermost', savings: 8, reason: 'Self-hosted option' }
      ],
      'Zoom': [
        { name: 'Google Meet', savings: 15, reason: 'Included with Google Workspace' },
        { name: 'Microsoft Teams', savings: 15, reason: 'Included with Office 365' },
        { name: 'Jitsi', savings: 20, reason: 'Open source, free' }
      ],
      'Notion': [
        { name: 'Confluence', savings: -5, reason: 'Better for enterprises' },
        { name: 'Obsidian', savings: 10, reason: 'One-time purchase' },
        { name: 'Coda', savings: 0, reason: 'Similar features' }
      ]
    };
    
    const suggestions = [];
    
    for (const sub of subscriptions) {
      if (alternatives[sub.vendor]) {
        suggestions.push({
          current: sub.vendor,
          currentCost: sub.cost,
          alternatives: alternatives[sub.vendor]
        });
      }
    }
    
    return suggestions;
  }
}

module.exports = UsageAnalytics;
