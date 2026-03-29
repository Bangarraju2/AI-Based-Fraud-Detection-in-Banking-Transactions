import React, { useState, useEffect } from 'react'
import { 
  BarChart3, TrendingUp, PieChart as PiIcon, Target, Brain 
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
  LineChart, Line, PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Radar,
} from 'recharts'
import { analyticsAPI } from '../services/api'

const DEMO_MONTHLY = Array.from({ length: 12 }, (_, i) => ({
  month: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i],
  transactions: Math.floor(Math.random() * 5000 + 3000),
  fraud: Math.floor(Math.random() * 100 + 20),
}))

const DEMO_HOURLY = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}:00`,
  fraud_count: Math.floor(Math.random() * 20 + (i >= 1 && i <= 5 ? 15 : 3)),
}))

const DEMO_MODEL = [
  { metric: 'Precision', score: 0.94 },
  { metric: 'Recall', score: 0.89 },
  { metric: 'F1 Score', score: 0.91 },
  { metric: 'ROC-AUC', score: 0.97 },
  { metric: 'Accuracy', score: 0.95 },
]

const RISK_DATA = [
  { name: 'High Risk', value: 234, color: '#ef4444' },
  { name: 'Medium Risk', value: 613, color: '#f59e0b' },
  { name: 'Low Risk', value: 47545, color: '#22c55e' },
]

const chartStyle = {
  backgroundColor: '#0f172a',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '12px',
  color: '#fff',
}

export default function AnalyticsPage() {
  const [monthly, setMonthly] = useState(DEMO_MONTHLY)
  const [hourly, setHourly] = useState(DEMO_HOURLY)
  const [model, setModel] = useState(DEMO_MODEL)
  const [riskDist, setRiskDist] = useState(RISK_DATA)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const { data } = await analyticsAPI.trends()
      if (data?.risk_distribution) {
        setRiskDist([
          { name: 'High Risk', value: data.risk_distribution.HIGH || 0, color: '#ef4444' },
          { name: 'Medium Risk', value: data.risk_distribution.MEDIUM || 0, color: '#f59e0b' },
          { name: 'Low Risk', value: data.risk_distribution.LOW || 0, color: '#22c55e' },
        ])
      }
    } catch { /* demo */ }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-gray-400 text-sm mt-1">Detailed fraud detection analytics and model performance</p>
      </div>

      {/* Top Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Transactions vs Fraud */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-brand-400" />
            <h3 className="text-lg font-semibold text-white">Monthly Overview</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={chartStyle} />
              <Legend />
              <Bar dataKey="transactions" fill="#6366f1" radius={[4, 4, 0, 0]} name="Transactions" />
              <Bar dataKey="fraud" fill="#ef4444" radius={[4, 4, 0, 0]} name="Fraud Cases" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Hourly Fraud Pattern */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-amber-400" />
            <h3 className="text-lg font-semibold text-white">Hourly Fraud Pattern</h3>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={hourly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={10} interval={2} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip contentStyle={chartStyle} />
              <Line type="monotone" dataKey="fraud_count" stroke="#f59e0b" strokeWidth={2.5} dot={{ fill: '#f59e0b', r: 3 }} name="Fraud Count" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bottom Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <PiIcon className="w-5 h-5 text-emerald-400" />
            <h3 className="text-lg font-semibold text-white">Risk Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={riskDist} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={5} dataKey="value">
                {riskDist.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={chartStyle} />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-2 mt-2">
            {riskDist.map((item, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-gray-400">{item.name}</span>
                </div>
                <span className="text-white font-medium">{item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Model Performance Radar */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-semibold text-white">Model Performance</h3>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={model}>
              <PolarGrid stroke="#1e293b" />
              <PolarAngleAxis dataKey="metric" stroke="#94a3b8" fontSize={11} />
              <PolarRadiusAxis domain={[0, 1]} tick={false} />
              <Radar name="Score" dataKey="score" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {model.map((m, i) => (
              <div key={i} className="text-center">
                <p className="text-xs text-gray-500">{m.metric}</p>
                <p className="text-sm font-bold text-white">{(m.score * 100).toFixed(1)}%</p>
              </div>
            ))}
          </div>
        </div>

        {/* Model Info Card */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-red-400" />
            <h3 className="text-lg font-semibold text-white">Model Info</h3>
          </div>
          <div className="space-y-4">
            {[
              { label: 'Active Model', value: 'XGBoost', tag: 'Best' },
              { label: 'Version', value: '20240315_143022' },
              { label: 'Training Samples', value: '45,000+' },
              { label: 'Features Used', value: '38' },
              { label: 'Last Retrained', value: 'Today' },
              { label: 'Detection Rate', value: '99.7%' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                <span className="text-sm text-gray-400">{item.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">{item.value}</span>
                  {item.tag && (
                    <span className="px-1.5 py-0.5 text-[10px] font-bold bg-emerald-500/20 text-emerald-400 rounded-md">{item.tag}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
