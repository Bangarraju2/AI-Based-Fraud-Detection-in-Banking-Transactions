import React, { useState, useEffect, useRef } from 'react'
import { ShieldAlert, Shield, CheckCircle, XCircle, Clock, AlertTriangle, Zap } from 'lucide-react'
import { fraudAPI } from '../services/api'

const DEMO_ALERTS = Array.from({ length: 15 }, (_, i) => ({
  id: i + 1,
  transaction_id: Math.floor(Math.random() * 10000) + 1,
  prediction_score: parseFloat((Math.random() * 0.5 + 0.5).toFixed(4)),
  risk_category: Math.random() > 0.4 ? 'HIGH' : 'MEDIUM',
  model_version: '20240315_143022',
  review_status: ['pending', 'confirmed_fraud', 'false_positive'][Math.floor(Math.random() * 3)],
  created_at: new Date(Date.now() - Math.random() * 3 * 86400000).toISOString(),
}))

export default function FraudAlertsPage() {
  const [alerts, setAlerts] = useState(DEMO_ALERTS)
  const [liveAlerts, setLiveAlerts] = useState([])
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState('all')
  const wsRef = useRef(null)

  useEffect(() => {
    loadAlerts()
    connectWebSocket()
    return () => wsRef.current?.close()
  }, [])

  const loadAlerts = async () => {
    try {
      setLoading(true)
      const { data } = await fraudAPI.alerts({ limit: 50 })
      if (data?.length) setAlerts(data)
    } catch { /* demo */ }
    finally { setLoading(false) }
  }

  const connectWebSocket = () => {
    try {
      const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const wsProtocol = apiBase.startsWith('https') ? 'wss:' : 'ws:'
      const wsHost = apiBase.replace(/^https?:\/\//, '')
      
      const ws = new WebSocket(`${wsProtocol}//${wsHost}/ws/alerts`)
      
      ws.onopen = () => console.log('WebSocket connected to', ws.url)
      ws.onmessage = (event) => {
        const alert = JSON.parse(event.data)
        if (alert.type === 'fraud_alert' || alert.type === 'new_transaction') {
          setLiveAlerts(prev => [alert, ...prev].slice(0, 10))
        }
      }
      ws.onclose = () => {
        console.warn('WebSocket disconnected. Retrying...')
        setTimeout(connectWebSocket, 5000)
      }
      wsRef.current = ws
    } catch (err) {
      console.error('WebSocket connection failed:', err)
    }
  }

  const simulateAlert = () => {
    const newAlert = {
      transaction_id: `txn_${Math.random().toString(36).substr(2, 9)}`,
      amount: Math.random() * 10000,
      fraud_score: 0.85 + Math.random() * 0.1,
      risk_category: 'HIGH',
      type: 'fraud_alert'
    }
    setLiveAlerts(prev => [newAlert, ...prev].slice(0, 10))
  }

  const handleReview = async (id, status) => {
    try {
      await fraudAPI.review(id, { review_status: status })
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, review_status: status } : a))
    } catch { 
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, review_status: status } : a))
    }
  }

  const filtered = filter === 'all' 
    ? alerts 
    : alerts.filter(a => a.review_status === filter)

  const statusIcon = (status) => {
    switch(status) {
      case 'confirmed_fraud': return <XCircle className="w-4 h-4 text-red-400" />
      case 'false_positive': return <CheckCircle className="w-4 h-4 text-emerald-400" />
      default: return <Clock className="w-4 h-4 text-amber-400" />
    }
  }

  const statusLabel = (status) => {
    switch(status) {
      case 'confirmed_fraud': return 'Confirmed Fraud'
      case 'false_positive': return 'False Positive'
      default: return 'Pending Review'
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Fraud Alerts</h1>
          <p className="text-gray-400 text-sm mt-1">Monitor and review flagged transactions</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={simulateAlert}
            className="flex items-center gap-2 px-3 py-1.5 glass-card text-xs text-amber-400 hover:bg-amber-400/10 transition-all border border-amber-400/20"
          >
            <Zap className="w-3.5 h-3.5" />
            Simulate Alert
          </button>
          <div className="flex items-center gap-2 px-3 py-1.5 glass-card text-xs">
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-gray-400">WebSocket</span>
            <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
          </div>
        </div>
      </div>

      {/* Live Alerts Banner */}
      {liveAlerts.length > 0 && (
        <div className="glass-card border-red-500/20 p-4 space-y-2">
          <h3 className="text-sm font-semibold text-red-400 flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            Live Alerts
          </h3>
          {liveAlerts.map((alert, i) => (
            <div key={i} className="flex items-center gap-4 p-3 bg-red-500/5 rounded-xl text-sm animate-slide-in">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span className="text-gray-300">Transaction <span className="text-white font-mono">{alert.transaction_id?.slice(0, 12)}</span></span>
              <span className="text-white font-semibold">${alert.amount?.toFixed(2)}</span>
              <span className="text-red-400 ml-auto">{(alert.fraud_score * 100).toFixed(1)}% risk</span>
            </div>
          ))}
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex gap-2">
        {[
          { key: 'all', label: 'All Alerts', count: alerts.length },
          { key: 'pending', label: 'Pending', count: alerts.filter(a => a.review_status === 'pending').length },
          { key: 'confirmed_fraud', label: 'Confirmed', count: alerts.filter(a => a.review_status === 'confirmed_fraud').length },
          { key: 'false_positive', label: 'Cleared', count: alerts.filter(a => a.review_status === 'false_positive').length },
        ].map(({ key, label, count }) => (
          <button 
            key={key}
            onClick={() => setFilter(key)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
              filter === key ? 'bg-brand-600 text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            {label}
            <span className={`px-1.5 py-0.5 rounded-md text-[10px] font-bold ${
              filter === key ? 'bg-white/20' : 'bg-white/5'
            }`}>{count}</span>
          </button>
        ))}
      </div>

      {/* Alert Cards */}
      <div className="grid gap-3">
        {filtered.map((alert) => (
          <div key={alert.id} className="glass-card p-5 flex items-center gap-5 hover:bg-white/[0.07] transition-all">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
              alert.risk_category === 'HIGH' ? 'bg-red-500/15' : 'bg-amber-500/15'
            }`}>
              <ShieldAlert className={`w-6 h-6 ${
                alert.risk_category === 'HIGH' ? 'text-red-400' : 'text-amber-400'
              }`} />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-1">
                <span className="font-semibold text-white">Alert #{alert.id}</span>
                <span className={`px-2 py-0.5 rounded-lg text-[10px] font-bold ${
                  alert.risk_category === 'HIGH' ? 'risk-high' : 'risk-medium'
                }`}>{alert.risk_category}</span>
              </div>
              <p className="text-sm text-gray-400">
                Transaction #{alert.transaction_id} • Score: <span className="text-white">{(alert.prediction_score * 100).toFixed(1)}%</span>
                {' • '}{new Date(alert.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 text-xs">
                {statusIcon(alert.review_status)}
                <span className="text-gray-300">{statusLabel(alert.review_status)}</span>
              </div>
              {alert.review_status === 'pending' && (
                <div className="flex gap-1.5">
                  <button
                    onClick={() => handleReview(alert.id, 'confirmed_fraud')}
                    className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-all" title="Confirm Fraud"
                  >
                    <XCircle className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleReview(alert.id, 'false_positive')}
                    className="p-2 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-all" title="Mark as False Positive"
                  >
                    <CheckCircle className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
