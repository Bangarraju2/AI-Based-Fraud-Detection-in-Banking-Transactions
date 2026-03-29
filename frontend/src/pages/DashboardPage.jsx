import React, { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { 
  Activity, AlertTriangle, ShieldCheck, TrendingUp, 
  ArrowUpRight, ArrowDownRight, Clock, Eye, Info,
  Zap, ChevronRight
} from 'lucide-react'
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'
import { analyticsAPI, authAPI } from '../services/api'
import socketService from '../services/socket'

const DEMO_KPI = {
  total_transactions: 48392,
  total_fraud_detected: 847,
  fraud_rate: 1.75,
  high_risk_count: 234,
  medium_risk_count: 613,
  low_risk_count: 47545,
  pending_reviews: 89,
  avg_fraud_score: 0.1247,
  transactions_today: 1283,
  fraud_today: 23,
}

const DEMO_TREND = Array.from({ length: 14 }, (_, i) => ({
  date: `Mar ${i + 10}`,
  transactions: Math.floor(Math.random() * 400 + 1000),
  fraud: Math.floor(Math.random() * 30 + 5),
}))

const PIE_COLORS = ['#ef4444', '#f59e0b', '#22c55e']

export default function DashboardPage() {
  const { user } = useAuth()
  const [kpis, setKpis] = useState(DEMO_KPI)
  const [trends, setTrends] = useState(DEMO_TREND)
  const [liveTransactions, setLiveTransactions] = useState([])
  const [loading, setLoading] = useState(false)
  const [wsStatus, setWsStatus] = useState('disconnected')

  useEffect(() => {
    loadData()
    
    // Connect to WebSocket
    socketService.connect()
    
    const unsubscribe = socketService.subscribe((message) => {
      if (message.type === 'status') {
        setWsStatus(message.connected ? 'connected' : 'disconnected')
      } else if (message.type === 'new_transaction') {
        handleNewTransaction(message)
      } else if (message.type === 'fraud_alert') {
        // Handle specialized fraud alerts if needed
        console.log('FRAUD ALERT:', message)
      }
    })

    return () => {
      unsubscribe()
      socketService.disconnect()
    }
  }, [])

  const handleNewTransaction = useCallback((tx) => {
    // Update KPIs
    setKpis(prev => ({
      ...prev,
      total_transactions: prev.total_transactions + 1,
      total_fraud_detected: tx.risk_category === 'HIGH' ? prev.total_fraud_detected + 1 : prev.total_fraud_detected,
      high_risk_count: tx.risk_category === 'HIGH' ? prev.high_risk_count + 1 : prev.high_risk_count,
      medium_risk_count: tx.risk_category === 'MEDIUM' ? prev.medium_risk_count + 1 : prev.medium_risk_count,
      low_risk_count: tx.risk_category === 'LOW' ? prev.low_risk_count + 1 : prev.low_risk_count,
      fraud_rate: Number(((prev.total_fraud_detected + (tx.risk_category === 'HIGH' ? 1 : 0)) / (prev.total_transactions + 1) * 100).toFixed(2)),
      transactions_today: prev.transactions_today + 1,
      fraud_today: tx.risk_category === 'HIGH' ? prev.fraud_today + 1 : prev.fraud_today
    }))

    // Add to live feed
    setLiveTransactions(prev => {
      const newFeed = [tx, ...prev]
      return newFeed.slice(0, 5) // Keep last 5
    })
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [dashRes, trendRes] = await Promise.allSettled([
        analyticsAPI.dashboard(),
        analyticsAPI.trends(),
      ])
      
      const success = dashRes.status === 'fulfilled' || trendRes.status === 'fulfilled'
      
      if (dashRes.status === 'fulfilled') setKpis(dashRes.value.data)
      if (trendRes.status === 'fulfilled') {
        const t = trendRes.value.data.trends
        if (t?.length) setTrends(t.map((d, i) => ({ 
          date: `Day ${i + 1}`, 
          transactions: d.total_transactions, 
          fraud: d.fraud_count 
        })))
      }

      if (success && user?.is_mock) {
        // Automatically exit mock mode if we successfully hit the API
        const updatedUser = { ...user, is_mock: false }
        localStorage.setItem('user', JSON.stringify(updatedUser))
        window.location.reload()
      }
    } catch (e) {
      // Use demo data
    } finally {
      setLoading(false)
    }
  }

  const handleConnectLive = async () => {
    setLoading(true)
    try {
      await authAPI.health()
      await loadData()
      socketService.connect()
    } catch (err) {
      alert("Backend still unreachable. Please ensure the FastAPI server is running on port 8000.")
    } finally {
      setLoading(false)
    }
  }

  const statCards = [
    { 
      title: 'Total Transactions', value: kpis.total_transactions?.toLocaleString(), 
      change: '+12.5%', up: true, icon: Activity, 
      gradient: 'from-blue-500/20 to-cyan-500/20', iconColor: 'text-blue-400'
    },
    { 
      title: 'Fraud Detected', value: kpis.total_fraud_detected?.toLocaleString(), 
      change: '-3.2%', up: false, icon: AlertTriangle, 
      gradient: 'from-red-500/20 to-orange-500/20', iconColor: 'text-red-400'
    },
    { 
      title: 'Fraud Rate', value: `${kpis.fraud_rate}%`, 
      change: '-0.3%', up: false, icon: ShieldCheck, 
      gradient: 'from-emerald-500/20 to-green-500/20', iconColor: 'text-emerald-400'
    },
    { 
      title: 'Pending Reviews', value: kpis.pending_reviews?.toLocaleString(), 
      change: '+5', up: true, icon: Eye, 
      gradient: 'from-amber-500/20 to-yellow-500/20', iconColor: 'text-amber-400'
    },
  ]

  const riskData = [
    { name: 'High Risk', value: kpis.high_risk_count },
    { name: 'Medium Risk', value: kpis.medium_risk_count },
    { name: 'Low Risk', value: kpis.low_risk_count },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Demo Mode Banner */}
      {user?.is_mock && (
        <div className="bg-brand-500/10 border border-brand-500/20 rounded-xl p-4 flex items-center justify-between animate-slide-in">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-brand-500/20 flex items-center justify-center text-brand-400">
              <Info className="w-5 h-5" />
            </div>
            <div>
              <p className="text-brand-300 font-semibold text-sm">Demo Mode Active</p>
              <p className="text-gray-400 text-xs">The system is using simulated data because the local backend is currently offline. All features are functional.</p>
            </div>
          </div>
          <button 
            onClick={handleConnectLive}
            disabled={loading}
            className="text-xs font-medium text-brand-400 hover:text-brand-300 px-3 py-1.5 rounded-lg border border-brand-500/30 hover:bg-brand-500/5 transition-all disabled:opacity-50"
          >
            {loading ? 'Connecting...' : 'Connect Live API'}
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Real-time fraud detection overview</p>
        </div>
        <div className="flex items-center gap-3">
          {wsStatus === 'connected' && (
            <div className="flex items-center gap-2 px-3 py-1.5 glass-card text-xs text-brand-400 border-brand-500/30">
              <Zap className="w-3.5 h-3.5 animate-pulse" />
              <span className="font-semibold uppercase tracking-wider">Live Stream Active</span>
            </div>
          )}
          <div className="flex items-center gap-2 px-3 py-1.5 glass-card text-xs text-gray-400">
            <Clock className="w-3.5 h-3.5" />
            <span>{user?.is_mock ? 'Simulated' : 'Live'} • Auto-refreshing</span>
            <span className={`w-2 h-2 rounded-full animate-pulse ${user?.is_mock ? 'bg-amber-500' : 'bg-emerald-500'}`}></span>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {statCards.map((card, i) => (
          <div key={i} className="stat-card animate-slide-in" style={{ animationDelay: `${i * 80}ms` }}>
            <div className="flex items-start justify-between mb-4">
              <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${card.gradient} flex items-center justify-center`}>
                <card.icon className={`w-5 h-5 ${card.iconColor}`} />
              </div>
              <span className={`flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-lg ${
                card.up ? 'bg-red-500/10 text-red-400' : 'bg-emerald-500/10 text-emerald-400'
              }`}>
                {card.up ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                {card.change}
              </span>
            </div>
            <p className="text-2xl font-bold text-white">{card.value}</p>
            <p className="text-sm text-gray-400 mt-1">{card.title}</p>
          </div>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Transaction Trend Chart */}
        <div className="lg:col-span-2 glass-card p-6 flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-white">Transaction & Fraud Trend</h3>
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-indigo-500"></div><span className="text-gray-400">Volume</span></div>
              <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-red-400"></div><span className="text-gray-400">Fraud</span></div>
            </div>
          </div>
          <div className="flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="gradTx" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradFraud" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', 
                    borderRadius: '12px', color: '#fff', fontSize: '12px'
                  }}
                />
                <Area type="monotone" dataKey="transactions" stroke="#6366f1" fill="url(#gradTx)" strokeWidth={2.5} name="Transactions" />
                <Area type="monotone" dataKey="fraud" stroke="#ef4444" fill="url(#gradFraud)" strokeWidth={2.5} name="Fraud" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Activity Feed */}
        <div className="glass-card flex flex-col">
          <div className="p-6 border-b border-white/5 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Live Traffic</h3>
            <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-emerald-500/10">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              Live
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="divide-y divide-white/5">
              {liveTransactions.length > 0 ? (
                liveTransactions.map((tx, i) => (
                  <div key={tx.transaction_id || i} className="p-4 hover:bg-white/5 transition-colors animate-slide-in">
                    <div className="flex items-center justify-between mb-2">
                        <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                            tx.risk_category === 'HIGH' ? 'bg-red-500/20 text-red-400' : 
                            (tx.risk_category === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-emerald-500/20 text-emerald-400')
                        }`}>
                            {tx.risk_category}
                        </span>
                        <span className="text-[10px] text-gray-500">{new Date(tx.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="flex items-center justify-between">
                        <div className="flex flex-col">
                            <span className="text-sm font-semibold text-white">${tx.amount?.toFixed(2)}</span>
                            <span className="text-[10px] text-gray-400 flex items-center gap-1">
                                <Zap className="w-3 h-3 text-brand-400" />
                                {tx.transaction_id.slice(0, 8)}...
                            </span>
                        </div>
                        <div className="flex flex-col items-end">
                            <span className="text-[10px] text-gray-500">Score</span>
                            <span className={`text-xs font-mono font-bold ${tx.risk_category === 'HIGH' ? 'text-red-400' : 'text-gray-300'}`}>
                                {tx.fraud_score?.toFixed(4)}
                            </span>
                        </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center p-8 text-center">
                    <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-4">
                        <Activity className="w-6 h-6 text-gray-600 animate-pulse" />
                    </div>
                    <p className="text-sm text-gray-500">Waiting for incoming traffic...</p>
                    <p className="text-[10px] text-gray-600 mt-2 italic">Run 'simulate_traffic.py' to see data flow</p>
                </div>
              )}
            </div>
          </div>
          {liveTransactions.length > 0 && (
            <div className="p-4 border-t border-white/5">
                <button className="w-full py-2 text-xs font-medium text-gray-400 hover:text-white flex items-center justify-center gap-2 group transition-all">
                    View Transaction History <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                </button>
            </div>
          )}
        </div>
      </div>

      {/* Risk Distribution & Footer Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Risk Distribution */}
        <div className="lg:col-span-1 glass-card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={riskData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={5} dataKey="value">
                {riskData.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i]} stroke="none" />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff' }} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-3 mt-4">
            {riskData.map((item, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[i] }}></div>
                  <span className="text-gray-400">{item.name}</span>
                </div>
                <span className="text-white font-mono font-medium">{item.value?.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Cards */}
        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="stat-card flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-400" />
            </div>
            <div>
                <p className="text-sm text-gray-400">Avg. Fraud Score</p>
                <p className="text-xl font-bold text-white">{(kpis.avg_fraud_score * 100).toFixed(2)}%</p>
            </div>
            </div>
            <div className="stat-card flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                <Activity className="w-6 h-6 text-blue-400" />
            </div>
            <div>
                <p className="text-sm text-gray-400">Today's Transactions</p>
                <p className="text-xl font-bold text-white">{kpis.transactions_today?.toLocaleString()}</p>
            </div>
            </div>
            <div className="stat-card flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-400" />
            </div>
            <div>
                <p className="text-sm text-gray-400">Fraud Today</p>
                <p className="text-xl font-bold text-white">{kpis.fraud_today}</p>
            </div>
            </div>
        </div>
      </div>
    </div>
  )
}

