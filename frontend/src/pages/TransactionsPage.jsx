import React, { useState, useEffect } from 'react'
import { ArrowLeftRight, Search, Filter, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react'
import { transactionsAPI } from '../services/api'

const DEMO_TRANSACTIONS = Array.from({ length: 20 }, (_, i) => ({
  id: i + 1,
  transaction_id: `txn_${Math.random().toString(36).substr(2, 12)}`,
  amount: parseFloat((Math.random() * 5000 + 10).toFixed(2)),
  time: Math.random() * 172800,
  fraud_score: parseFloat((Math.random()).toFixed(4)),
  risk_category: ['LOW', 'LOW', 'LOW', 'MEDIUM', 'HIGH'][Math.floor(Math.random() * 5)],
  is_fraud: Math.random() > 0.85,
  is_flagged_for_review: Math.random() > 0.7,
  created_at: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
}))

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState(DEMO_TRANSACTIONS)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(485)
  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [loading, setLoading] = useState(false)
  const perPage = 20

  useEffect(() => { loadTransactions() }, [page, riskFilter])

  const loadTransactions = async () => {
    try {
      setLoading(true)
      const params = { page, per_page: perPage }
      if (riskFilter) params.risk_category = riskFilter
      const { data } = await transactionsAPI.list(params)
      if (data.transactions?.length) {
        setTransactions(data.transactions)
        setTotal(data.total)
      }
    } catch {
      // Use demo data
    } finally {
      setLoading(false)
    }
  }

  const filteredTx = search
    ? transactions.filter(t => 
        t.transaction_id.includes(search) || 
        t.amount.toString().includes(search)
      )
    : transactions

  const riskBadge = (risk) => {
    const cls = risk === 'HIGH' ? 'risk-high' : risk === 'MEDIUM' ? 'risk-medium' : 'risk-low'
    return <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${cls}`}>{risk}</span>
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Transactions</h1>
          <p className="text-gray-400 text-sm mt-1">{total.toLocaleString()} total transactions</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-11"
            placeholder="Search by ID or amount..."
          />
        </div>
        <div className="flex gap-2">
          {['', 'LOW', 'MEDIUM', 'HIGH'].map((f) => (
            <button 
              key={f} 
              onClick={() => { setRiskFilter(f); setPage(1) }}
              className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                riskFilter === f 
                  ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/25' 
                  : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
              }`}
            >
              {f || 'All'}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left py-4 px-6 text-gray-400 font-medium">Transaction ID</th>
                <th className="text-left py-4 px-4 text-gray-400 font-medium">Amount</th>
                <th className="text-left py-4 px-4 text-gray-400 font-medium">Fraud Score</th>
                <th className="text-left py-4 px-4 text-gray-400 font-medium">Risk Level</th>
                <th className="text-left py-4 px-4 text-gray-400 font-medium">Status</th>
                <th className="text-left py-4 px-4 text-gray-400 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {filteredTx.map((tx) => (
                <tr key={tx.id} className="table-row">
                  <td className="py-3.5 px-6">
                    <div className="flex items-center gap-2">
                      <ArrowLeftRight className="w-4 h-4 text-gray-500" />
                      <span className="font-mono text-gray-300 text-xs">{tx.transaction_id.slice(0, 16)}...</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-semibold text-white">${tx.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${
                            tx.fraud_score > 0.7 ? 'bg-red-500' : tx.fraud_score > 0.3 ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${tx.fraud_score * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-gray-300 text-xs">{(tx.fraud_score * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">{riskBadge(tx.risk_category)}</td>
                  <td className="py-3.5 px-4">
                    {tx.is_fraud ? (
                      <span className="px-2 py-1 text-xs font-medium rounded-lg bg-red-500/10 text-red-400">Fraud</span>
                    ) : tx.is_flagged_for_review ? (
                      <span className="px-2 py-1 text-xs font-medium rounded-lg bg-amber-500/10 text-amber-400">Review</span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium rounded-lg bg-emerald-500/10 text-emerald-400">Clear</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-gray-400 text-xs">
                    {new Date(tx.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-white/5">
          <p className="text-sm text-gray-400">
            Showing {((page - 1) * perPage) + 1}–{Math.min(page * perPage, total)} of {total}
          </p>
          <div className="flex gap-2">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1} className="btn-secondary py-2 px-3 disabled:opacity-30">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button onClick={() => setPage(page + 1)} disabled={page * perPage >= total} className="btn-secondary py-2 px-3 disabled:opacity-30">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
