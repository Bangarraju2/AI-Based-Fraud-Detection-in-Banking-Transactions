/**
 * WebSocket Service
 * Manages real-time connection to the FraudShield backend.
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000;
    this.url = null;
  }

  connect(url) {
    if (this.ws && this.ws.readyState <= 1) return;
    
    this.url = url || this.getDefaultUrl();
    console.log(`Connecting to WebSocket: ${this.url}`);
    
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket Connected');
        this.reconnectAttempts = 0;
        this.broadcast({ type: 'status', connected: true });
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.broadcast(data);
        } catch (e) {
          console.error('Error parsing WS message:', e);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket Disconnected');
        this.broadcast({ type: 'status', connected: false });
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
      };
    } catch (e) {
      console.error('WebSocket Connection Error:', e);
      this.attemptReconnect();
    }
  }

  getDefaultUrl() {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // If VITE_API_URL is an absolute URL, replace protocol
    if (apiBase.startsWith('http')) {
        const base = apiBase.replace(/\/$/, ''); // Remove trailing slash
        return base.replace(/^http/, 'ws') + '/api/ws/alerts';
    }
    
    // Fallback/Relative
    const host = window.location.host;
    return `${wsProto}//${host}/api/ws/alerts`;
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting reconnect ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectInterval}ms...`);
      setTimeout(() => this.connect(this.url), this.reconnectInterval);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  subscribe(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  broadcast(data) {
    this.listeners.forEach(callback => callback(data));
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }
}

const socketService = new WebSocketService();
export default socketService;
