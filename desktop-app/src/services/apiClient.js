const axios = require('axios');

class APIClient {
  constructor(baseURL, authToken) {
    this.baseURL = baseURL || 'http://localhost:8000';
    this.authToken = authToken;
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add auth interceptor
    this.client.interceptors.request.use((config) => {
      if (this.authToken) {
        config.headers.Authorization = `Bearer ${this.authToken}`;
      }
      return config;
    });
  }

  setAuthToken(token) {
    this.authToken = token;
  }

  async uploadEmailReceipt(emailData) {
    try {
      const response = await this.client.post('/api/v1/emails/scan', emailData);
      return response.data;
    } catch (error) {
      console.error('Email upload error:', error.response?.data || error.message);
      throw error;
    }
  }

  async uploadSMSTransaction(smsData) {
    try {
      const response = await this.client.post('/api/v1/sms/parse', smsData);
      return response.data;
    } catch (error) {
      console.error('SMS upload error:', error.response?.data || error.message);
      throw error;
    }
  }

  async uploadScannedDocument(documentData) {
    try {
      const response = await this.client.post('/api/v1/documents/scan', documentData);
      return response.data;
    } catch (error) {
      console.error('Document upload error:', error.response?.data || error.message);
      throw error;
    }
  }

  async getSubscriptions() {
    try {
      const response = await this.client.get('/api/v1/subscriptions/');
      return response.data;
    } catch (error) {
      console.error('Get subscriptions error:', error.response?.data || error.message);
      throw error;
    }
  }

  async createCalendarEvent(eventData) {
    try {
      const response = await this.client.post('/api/v1/calendar/events', eventData);
      return response.data;
    } catch (error) {
      console.error('Calendar event error:', error.response?.data || error.message);
      throw error;
    }
  }
}

module.exports = APIClient;
